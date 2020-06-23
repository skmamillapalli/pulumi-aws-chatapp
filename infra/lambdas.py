from pulumi_aws import lambda_
from pulumi import Config, AssetArchive, FileArchive
import os

def create_lambda_layers(appcode_path):
    layer_path=os.path.join(appcode_path, 'chatapp-source/app-layers')

    # Create lambda layers
    lambda_layer = lambda_.LayerVersion(
    "helper-layers",
    layer_name="chatapp-pythonlibraries",
    code=AssetArchive({
            '.': FileArchive(layer_path)
        }),
    compatible_runtimes=['python3.8', 'python2.7']
    )   
    return lambda_layer

def create_functions(appcode_path=None,
        region=None,
        account=None,
        stage=None,
        lambda_execution_role=None,
        lambda_layers=None,
        subnets=None,
        lambda_sg=None,
        redis_cluster=None,
        rds_instance=None,
        web_socket_api=None):
    """Create backend functions for Apigw"""
    # Construct callback_url
    callback_url = web_socket_api.id.apply(
        lambda id: "https://{}.execute-api.{}.amazonaws.com/{}/".format(id,region.name,stage)
    )
    rds_config = Config().require_object("rds_config")
    # create lambda permission for Apigateway invocations
    route_arn = web_socket_api.id.apply(
        lambda id: "arn:aws:execute-api:{}:{}:{}/*/*".format(region.name, account, id)
    )

    send_message_path = os.path.join(appcode_path, 'chatapp-source/sendmessage')
    send_message_function = lambda_.Function(
        "sendmessagefunction",
        role=lambda_execution_role.arn,
        handler='lambda_handler.lambda_handler',
        description="Backend lambda to handle messaging",
        runtime='python3.8',
        code=AssetArchive({
            '.': FileArchive(send_message_path)
        }),
        layers=[lambda_layers.arn],
        timeout=10,
        vpc_config={
            "securityGroupIds": [lambda_sg.id],
            "subnetIds": [subnet.id for subnet in subnets]
        },
        environment={
            "variables":{
            "redis_hostname": redis_cluster.cache_nodes[0]['address'],
            "redis_port": '6379',
            "redis_password": '',
            "callbackurl": callback_url
            }}
        )


    connect_path = os.path.join(appcode_path, 'chatapp-source/connect')
    connect_function = lambda_.Function(
        "connectfunction",
        role=lambda_execution_role.arn,
        handler='lambda_handler.lambda_handler',
        description="Backend lambda to handle Auth/connections.",
        runtime='python3.8',
        code=AssetArchive({
            '.': FileArchive(connect_path)
        }),
        layers=[lambda_layers.arn],
        timeout=10,
        vpc_config={
            "securityGroupIds": [lambda_sg.id],
            "subnetIds": [subnet.id for subnet in subnets]
        },
        environment={
            "variables":{
            "redis_hostname": redis_cluster.cache_nodes[0]['address'],
            "redis_port": '6379',
            "redis_password": '',
            "callbackurl": callback_url,
            "rds_hostname": rds_instance.address,
            "rds_port": '3306',
            "rds_password": rds_config["password"],
            "rds_database": rds_config["database_name"],
            "rds_user": rds_config["username"]
            }
        }
        )

    disconnect_path = os.path.join(appcode_path, 'chatapp-source/disconnect')
    disconnect_function = lambda_.Function(
        "disconnectfunction",
        role=lambda_execution_role.arn,
        handler='lambda_handler.lambda_handler',
        description="Backend lambda to handle post connection termination.",
        runtime='python3.8',
        code=AssetArchive({
            '.': FileArchive(disconnect_path)
        }),
        layers=[lambda_layers.arn],
        timeout=10,
        vpc_config={
            "securityGroupIds": [lambda_sg.id],
            "subnetIds": [subnet.id for subnet in subnets]
        },
        environment={
            "variables":{
            "redis_hostname": redis_cluster.cache_nodes[0]['address'],
            "redis_port": '6379',
            "redis_password": ''
            }
        }
        )

    lambda_.Permission(
        "lambdainvocationpermissions",
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        function=send_message_function.id,
        source_arn=route_arn
    )

    lambda_.Permission(
        "lambdainvocationpermissions-1",
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        function=connect_function.id,
        source_arn=route_arn
    )

    lambda_.Permission(
        "lambdainvocationpermissions-2",
        action="lambda:InvokeFunction",
        principal="apigateway.amazonaws.com",
        function=disconnect_function.id,
        source_arn=route_arn
    )
    return {
        "connect": connect_function,
        "disconnect": disconnect_function,
        "sendmessage": send_message_function
    }
