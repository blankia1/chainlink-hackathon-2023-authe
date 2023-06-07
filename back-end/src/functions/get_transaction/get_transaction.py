import os
import json
import logging
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from decimal import Decimal

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['TransactionsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    if 'pathParameters' in event:
        hash =  event['pathParameters'].get('transaction_hash')
    else:
        hash = event['transaction_hash']

    LOGGER.info(hash)
    LOGGER.info("hash given is:" +  hash)

    # Query item for only PK the transactions from Dynamodb table
    try:
        response = client.query(
            TableName=DYNAMO_DB_TABLE_NAME,
            ExpressionAttributeValues={
                ':hash': {"S": hash}
            },
            KeyConditionExpression='#hash = :hash',
            ExpressionAttributeNames={
                '#hash': 'hash'
            }
        )
    except Exception as err:
        LOGGER.error('Error retrieving the transaction: %s' % err)
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
        }),
    } 

    found_item = response['Items']

    # No transactions found at all
    LOGGER.info("Found number of transactions: " + str(len(found_item)))
    if len(found_item) == 0:
        LOGGER.warning("No transactions found for hash: " + hash)
        return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "not_found",
                    "reason": "No transactions found",
                    "detailed_reason": "No transactions found for hash: " + hash
            }),
        } 

    parsed_item = dynamo_obj_to_python_obj(found_item[0])
    
    return {
        'statusCode': 200,
        'body': json.dumps(parsed_item, cls=DecimalEncoder),

        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)
    