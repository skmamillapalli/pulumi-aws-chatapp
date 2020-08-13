import json
import os,sys
import boto3
sys.path.insert(0, '/opt')
import redis, urllib

def lambda_handler(event, context):
    # TODO implement
    # Get connection Id
    print(context, event)

    body = json.loads(event['body'])
    sendTo = body['to']
    message = body['message']
    redis_hostname = os.environ.get('redis_hostname')
    redis_port = os.environ.get('redis_port')
    redis_password = os.environ.get('redis_password')
    r = redis.Redis(
        host=redis_hostname,
        port=redis_port, 
        password=redis_password)
    try:
        client = boto3.client('apigatewaymanagementapi',
                               endpoint_url = str(os.environ.get('callbackurl')))
        connection_id = r.get(sendTo)
        print("Send message to {}".format(connection_id))
        response = client.post_to_connection(
            Data=json.dumps(message).encode('utf-8'),
            ConnectionId=connection_id.decode('utf-8'))
        print(response)
    except Exception as e:
        print(e)
        return {
            'statusCode': '401'
        }
    return {
        'statusCode': 200,
        'body': json.dumps('Message sent!')
    }
