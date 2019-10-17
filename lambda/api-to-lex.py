import json
import boto3

def lambda_handler(event, context):
    userId = event['userId']
    print(userId)
    message = event['message']
    client = boto3.client('lex-runtime')
    response = client.post_text(
    botName = 'DiningConcierge',
    botAlias = 'initial',
    userId = userId,
    inputText = message)
    print("Response::: ",response)
    return response