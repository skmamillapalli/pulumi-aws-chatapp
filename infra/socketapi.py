from pulumi_aws import apigatewayv2
import random, string, sys, os

def create_websocket_api():
    api_description = "APIs for a simple chat application"+"-"+''.join(random.sample(string.ascii_lowercase, 10))
    
    # Create an APiGatewayv2 Websocket API
    web_socket_api = apigatewayv2.Api(
    "ChatAppApi",
    protocol_type="WEBSOCKET",
    description=api_description,
    route_selection_expression="$request.body.action",
    tags={"Category":"Test"},
    version="v1"
)
    return {
        "api": web_socket_api,
        "description": api_description
    }

def create_route_integrations(region=None, web_socket_api=None, functions=None, description=None):
    # Create integration arn
    connect_function=functions['connect']
    disconnect_function=functions['disconnect']
    send_message_function=functions['sendmessage']
    connect_integration_arn=connect_function.arn.apply(
        lambda arn: 'arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations'.format(region.name,arn)
    )
    disconnect_integration_arn=disconnect_function.arn.apply(
        lambda arn: 'arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations'.format(region.name,arn)
    )
    send_message_integration_arn=send_message_function.arn.apply(
        lambda arn: 'arn:aws:apigateway:{}:lambda:path/2015-03-31/functions/{}/invocations'.format(region.name,arn)
    )

    # Create integration with backend lambda
    connect_integration_id = apigatewayv2.Integration("connectroute",
        api_id=web_socket_api.id,
        integration_type="AWS_PROXY",
        integration_uri=connect_integration_arn,
        integration_method="POST").id.apply(
            lambda integration: 'integrations/'+integration
        )

    disconnect_integration_id = apigatewayv2.Integration("disconnectroute",
        api_id=web_socket_api.id,
        integration_type="AWS_PROXY",
        integration_uri=disconnect_integration_arn,
        integration_method="POST").id.apply(
          lambda integration: 'integrations/'+integration
        )

    send_message_integration_id = apigatewayv2.Integration("sendmessageroute",
        api_id=web_socket_api.id,
        integration_type="AWS_PROXY",
        integration_uri=send_message_integration_arn,
        integration_method="POST").id.apply(
            lambda integration: 'integrations/'+integration
        )

    # Create routes
    # -------------
    # Hacky way to get around connect/disconnect updates
    # pulumi won't let update routes created by default and this is stopping from adding a backend integrations
    # This fix will be removed once a way is figured out
    sys.path.insert(0, os.path.join(os.path.curdir, 'packages'))
    import boto3
    client = boto3.client('apigatewayv2')
    apis=client.get_apis()['Items']
    boto_api_id=None
    for api in apis:
        if api.get('Description', None) == description:
            boto_api_id = api['ApiId']
    if boto_api_id:
        routes = client.get_routes(ApiId=boto_api_id)['Items']
        for route in routes:
            # Just set target once, let pulumi manage after that
            if not 'Target' in route:
                client.delete_route(ApiId=boto_api_id,
                RouteId=route['RouteId'])
    sys.path.pop(0)

    connect_route = apigatewayv2.Route("connect-route",
        api_id=web_socket_api.id,
        route_key="$connect",
        target=connect_integration_id)

    disconnect_route = apigatewayv2.Route("disconnect-route",
        api_id=web_socket_api.id,
        route_key="$disconnect",
        target=disconnect_integration_id)

    send_message_route = apigatewayv2.Route("sendmessage-route",
        api_id=web_socket_api.id,
        route_key="send",
        target=send_message_integration_id)

def create_deployment(web_socket_api=None):
    deployment=apigatewayv2.Deployment("example",
        api_id=web_socket_api.id,
        description="ChatApp API deployment")
    return deployment

def create_stage(stage=None, web_socket_api=None, deployment=None):
    stage = apigatewayv2.Stage("Devstage",
        api_id=web_socket_api.id,
        name=stage,
        deployment_id=deployment.id)
    return stage