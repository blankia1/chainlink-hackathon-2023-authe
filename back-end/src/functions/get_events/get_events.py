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
    DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    if 'multiValueQueryStringParameters' in event:
        addresses =  event['multiValueQueryStringParameters'].get('address')
    else:
        addresses = event['address']

    LOGGER.info("Number of addresses: " + str(len(addresses)))
    LOGGER.info(addresses)
    LOGGER.info("Addresses given are: {}".format(' '.join(map(str, addresses))))

    found_items = []
    for address in addresses:
        # Query the event from Dynamodb table
        LOGGER.info("Retrieving the events for address: " + address)
        try:
            response = client.query(
                TableName=DYNAMO_DB_TABLE_NAME,
                ExpressionAttributeValues={
                    ':address': {"S": address.lower() },
                },
                KeyConditionExpression='address = :address',
                ScanIndexForward=False
            )
            found_items += response['Items']
        except Exception as err:
            LOGGER.error('Error retrieving the transactions: %s' % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": err.args[0],
                    "detailed_reason": err.args[1:]
            }),
        } 
        LOGGER.info("Found number of events for address: " + address + ": " + str(len(response['Items'])))
        

    # Check if all events have been found at all
    # No events found at all
    LOGGER.info("Found number of events in total: " + str(len(found_items)))
    
    parsed_items = []
    found_addresses = []
    for item in found_items:
        parsed_item = dynamo_obj_to_python_obj(item)
        parsed_items.append(parsed_item)
        # LOGGER.info(parsed_item)
        found_addresses.append(parsed_item.get('address'))

    # Check if all transactions have been found for the addresses provided
    not_found_addresses = []
    for address in addresses:
        if address not in found_addresses: 
            not_found_addresses.append(address)

    if not_found_addresses != []:
        LOGGER.warning("No transactions found for addresses: " + ' '.join(map(str, not_found_addresses)))
    
    return {
        'statusCode': 200,
        'body': json.dumps(parsed_items, cls=DecimalEncoder),

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
    