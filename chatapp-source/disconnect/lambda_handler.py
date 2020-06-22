import json
import boto3
import sys,os
sys.path.insert(0, '/opt/')
import pymysql
import redis

def lambda_handler(event, context):
    # TODO implement
    print(event, context)
    connectionId = event['requestContext']['connectionId']

    # Remove connectionId in redis
    redis_hostname = os.environ.get('redis_hostname')
    redis_port = os.environ.get('redis_port')
    redis_password = os.environ.get('redis_password')
    r = redis.Redis(
    host=hostname,
    port=port, 
    password=password)
    # print(r)
    # r.delete('user')
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }