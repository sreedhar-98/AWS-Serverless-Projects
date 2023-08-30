import json
import boto3
import os



def lambda_handler(event,context):
    try:
        dynamo=boto3.client('dynamodb')
        connectionId=event["requestContext"]["connectionId"]
        message=json.loads(event['body'])['Message']
        endpoint_url=os.environ['endpointurl']
        table_name=os.environ['TableName']
        api_resp=boto3.client('apigatewaymanagementapi',endpoint_url=endpoint_url)
        query_params ={
            'TableName': table_name,
            'KeyConditionExpression': 'connectionId = :connId',
            'ExpressionAttributeValues': {
                ':connId': {'S': connectionId}  
            },
            'ProjectionExpression':'roomId'
        }
        response=dynamo.query(**query_params)['Items']
        if not response:
            api_resp.post_to_connection(ConnectionId=connectionId,Data=json.dumps("Please join a room or create a room to send message!!").encode('utf-8'))
            #return {"statusCode":404}
        else:
            roomId=response[0]['roomId']['S']
            query_params = {
                'TableName': table_name,
                'IndexName': 'roomId-index', 
                'KeyConditionExpression': 'roomId = :room_id_val',
                'ExpressionAttributeValues': {
                    ':room_id_val': {'S': roomId}
                },
                'ProjectionExpression':'connectionId'
            }
            users=dynamo.query(**query_params)['Items']
            for user in users:
                conn_id=user['connectionId']['S']
                if conn_id!=connectionId:
                    api_resp.post_to_connection(ConnectionId=conn_id,Data=json.dumps(connectionId+" : "+message).encode('utf-8'))
            s=f"Message sent successfully by {connectionId}"
            print(s)
        return {"statusCode":200}
       
    except Exception as e:
        print("Error occured!!",e)
        return {"statusCode":500}
    