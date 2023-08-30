import json
import boto3
import os




def lambda_handler(event,context):
    try:
        dynamo=boto3.client('dynamodb')
        roomId=json.loads(event['body'])['roomId']
        connectionId=event["requestContext"]["connectionId"]
        endpoint_url=os.environ['endpointurl']
        table_name=os.environ['TableName']
        api_resp=boto3.client('apigatewaymanagementapi',endpoint_url=endpoint_url)
        query_params = {
            'TableName': table_name,
            'IndexName': 'roomId-index', 
            'KeyConditionExpression': 'roomId = :room_id_val',
            'ExpressionAttributeValues': {
                ':room_id_val': {'S': roomId}  
            }
        }
        response=dynamo.query(**query_params)['Items']
        if len(response)==0:
            api_resp.post_to_connection(ConnectionId=connectionId,Data=json.dumps("Room does not exist!!").encode('utf-8'))
        else:
            chatAppTable=boto3.resource('dynamodb').Table(table_name)
            chatAppTable.put_item(

                Item={
                    "connectionId":connectionId,
                    "roomId":roomId,
                    "creator":0
                }
            )
            api_resp.post_to_connection(ConnectionId=connectionId,Data=json.dumps("Successfully joined the room!!").encode('utf-8'))
        print(f"User with {connectionId} joined the room {roomId}")
        return {"statusCode":200}
    except Exception as e:
        print("Error occured!!",e)
        return {"statusCode":500}
    
