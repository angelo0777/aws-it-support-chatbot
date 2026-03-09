import json
import boto3
import uuid
from datetime import datetime

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
faq_table = dynamodb.Table('ITSupportFAQ')
log_table = dynamodb.Table('ChatbotLogs')

def lambda_handler(event, context):

    # Get user query
    query = event['inputTranscript'].lower()

    try:
        # Search FAQ table
        response = faq_table.get_item(
            Key={'question': query}
        )

        if 'Item' in response:
            answer = response['Item']['answer']
        else:
            answer = "I couldn't find a solution. Your query will be forwarded to IT support."

    except Exception as e:
        answer = "Error accessing the knowledge base."

    # Log user query
    log_table.put_item(
        Item={
            'query_id': str(uuid.uuid4()),
            'query': query,
            'timestamp': datetime.now().isoformat()
        }
    )

    intent_name = event['sessionState']['intent']['name']

    return {
        "sessionState": {
            "dialogAction": {
                "type": "Close"
            },
            "intent": {
                "name": intent_name,
                "state": "Fulfilled"
            }
        },
        "messages": [
            {
                "contentType": "PlainText",
                "content": answer
            }
        ]
    }
