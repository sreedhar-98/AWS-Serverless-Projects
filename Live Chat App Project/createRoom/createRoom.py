import boto3
import json
import time
import random
import string
import os


def lambda_handler(event,context):
    try:
        dynamo=boto3.client('dynamodb')
        connectionId=event["requestContext"]["connectionId"]
        endpoint_url=os.environ['endpointurl']
        table_name=os.environ['TableName']
        api_resp=boto3.client('apigatewaymanagementapi',endpoint_url=endpoint_url)
        timestamp_part = str(int(time.time()))
        random_part = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        roomId=timestamp_part+random_part
        chatAppTable=boto3.resource('dynamodb').Table(table_name)
        resp=chatAppTable.put_item(
            Item={
                "connectionId":connectionId,
                "roomId":roomId,
                "creator":1
            }
        )
        print(resp)
        response=api_resp.post_to_connection(ConnectionId=connectionId,Data=json.dumps("Room created with ID : "+roomId).encode('utf-8'))
        print(f"Room is created with id {roomId} for {connectionId}")
        return {
        "statusCode":200
        } 
    except Exception as e:
        print("Error Occured!!",e)
        return {"statusCode":500}