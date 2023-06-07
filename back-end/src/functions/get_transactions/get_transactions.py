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

    if 'multiValueQueryStringParameters' in event:
        addresses =  event['multiValueQueryStringParameters'].get('address')
        chain =  event['queryStringParameters'].get('chain', 'sepolia')
    else:
        addresses = event['address']
        chain =  event.get('chain', 'sepolia')

    LOGGER.info(addresses)
    LOGGER.info("Addresses given are: {}".format(' '.join(map(str, addresses))))
    LOGGER.info("For chain: {}".format(chain))

    found_items = []
    for address in addresses:
        # Batch item Get the permission documents from Dynamodb table
        LOGGER.info("Retrieving the transactions")
        try:
            response = client.query(
                TableName=DYNAMO_DB_TABLE_NAME,
                IndexName='transactions-address-block-index',
                KeyConditionExpression='address = :address',
                FilterExpression='chain = :chain',
                ExpressionAttributeValues={
                    ':address': {"S": address.lower() },
                    ':chain': {"S": chain },
                },
                ScanIndexForward=False,
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

    # Check if all transactions have been found
    # No transactions found at all
    LOGGER.info("Found number of transactions: " + str(len(found_items)))
    
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
        LOGGER.warning("No transactions found for addresses: " + ' '.join(map(str, not_found_addresses)) + " and chain: " + chain)
    
    # dynamodb = boto3.resource('dynamodb', region_name=region)
    # table = dynamodb.Table(DYNAMO_DB_TABLE_NAME)
    # response = table.scan()
    # data = response['Items']

    # while 'LastEvaluatedKey' in response:
    #     response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    #     data.extend(response['Items'])

    # print(data)
    # print("count total")
    # print(len(data))

    return {
        'statusCode': 200,
        # 'body': json.dumps({"found_permission_documents": parsed_items, "not_found_permission_documents": not_found_addresses}, cls=DecimalEncoder),
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
    