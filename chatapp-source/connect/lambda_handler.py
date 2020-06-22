import json
import boto3
import sys,os
sys.path.insert(0, '/opt/')
import pymysql
import redis

def lambda_handler(event, context):
    
    username = event['headers']['username']
    connectionId = event['requestContext']['connectionId']
    
    # Get rds creds from environment
    rds_hostname = os.environ.get('rds_hostname')
    rds_port = os.environ.get('rds_port')
    # To-do: manage password via ssm
    rds_password = os.environ.get('rds_password')
    rds_user = os.environ.get('rds_user')
    rds_database = os.environ.get('rds_database')
    
    #See if user is registered
    connection = pymysql.connect(host=rds_hostname,
                             user=rds_user,
                             password=rds_password,
                             db='chatapp',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor=connection.cursor()
    
    registered=True
    
    # Create table and fill-up users, this users are counted as registered users and can use chatapp service
    # ----------------------------------------------
    # sqlQuery="CREATE TABLE Users(user_id int, LastName varchar(32), FirstName varchar(32), MobileNumber int)"
    # cursor.execute(sqlQuery)
    # cursor.executemany("insert into Users (user_id, LastName, FirstName, MobileNumber) values (%s, %s, %s, %s)",
    # [(1, 'Mamillapalli', 'Sunil', 1111), (3,'Musk', 'Elon', 3333), (4, 'Ram', 'Alok', 4444),(5,'Sam','Smith',5555)])
    # connection.commit()
    
    # Uncomment following section only after registered users functionality is handled manually like above or via API
    # ------------------------------------------------------------------------------------------------------------------
    # cursor.execute("select * from Users")
    # registered = False
    # for row in cursor.fetchall():
    #     print(username, row['FirstName'])
    #     if username in row['FirstName'] or username in row['LastName']:
    #         registered = True
    #         break
    if registered:
        # store connectionId in redis
        redis_hostname = os.environ.get('redis_hostname')
        redis_port = os.environ.get('redis_port')
        redis_password = os.environ.get('redis_password')
        r = redis.Redis(
        host=redis_hostname,
        port=redis_port, 
        password=redis_password)
        r.set(username, connectionId)
        print(r.get(username))
        return {
        'statusCode': 200,
        'body': 'Connected!'
        }
    else:
        return{
            'statusCode': 401,
            'body': 'Cannot identify user.'
        }
