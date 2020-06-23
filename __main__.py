import infra.network as network
import infra.storage as storage
import infra.iam as iam
import infra.lambdas as lambdas
import infra.socketapi as socketapi
import os, sys
from pulumi import Config
from pulumi import export
from pulumi_aws import get_region, get_caller_identity

region=get_region()
account=get_caller_identity().account_id
appcode_path=os.environ.get("CHATAPP_LIB", None)
stage_config = Config().require_object("stage_config")
if not appcode_path:
    appcode_path=os.path.curdir
vpc_details = network.setup_vpc()
security_groups = network.create_firewall_rules(vpc_details['vpc'])
storage_nodes = storage.create_storage_nodes(vpc_details['private_subnets'], security_groups)
lambda_roles = iam.create_lambda_execution_roles(region, account)
lambda_layer = lambdas.create_lambda_layers(appcode_path)
socket_api = socketapi.create_websocket_api()
lambda_functions = lambdas.create_functions(appcode_path=appcode_path,
        region=region,
        account=account,
        stage=stage_config['stage'],
        lambda_execution_role=lambda_roles['role'],
        lambda_layers=lambda_layer,
        subnets=vpc_details['private_subnets'],
        lambda_sg=security_groups['lambda_sg'],
        redis_cluster=storage_nodes['redis'],
        rds_instance=storage_nodes['rds'],
        web_socket_api=socket_api['api'])
deployment = socketapi.create_route_integrations(
    web_socket_api=socket_api['api'],
    functions=lambda_functions,
    region=region,
    description=socket_api['description']
)

# Finally create a Stage
stage = socketapi.create_stage(
    stage=stage_config['stage'],
    web_socket_api=socket_api['api'],
    deployment=deployment)

# and export outputs
export("invoke_url", stage.invoke_url.apply(lambda url:url+'/'))

export("callback_url",socket_api['api'].id.apply(
        lambda id: "https://{}.execute-api.{}.amazonaws.com/{}/".format(id,region.name,stage_config['stage'])
    ))








