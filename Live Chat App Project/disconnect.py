import json
import boto3


def lambda_handler(event, context):
    try:
        dynamo=boto3.client('dynamodb')
        connectionId=event["requestContext"]["connectionId"]
        query_params ={
            'TableName': "ChatAppData",
            'KeyConditionExpression': 'connectionId = :connId',
            'ExpressionAttributeValues': {
                ':connId': {'S': connectionId}  
            },
            'ProjectionExpression':'roomId'
        }
        response=dynamo.query(**query_params)['Items']
        roomId=response[0]['roomId']['S']
        response=dynamo.delete_item(
            TableName="ChatAppData",
            Key={
                "connectionId":{"S":connectionId},
                "roomId":{"S":roomId}
            }
            )
        s=f"connectionId : {connectionId} disconnected successfully!!"
        print(s)
        return {"statusCode":200}
    except Exception as e:
        print("Error occures: ",e)
        return {"statusCode":500}