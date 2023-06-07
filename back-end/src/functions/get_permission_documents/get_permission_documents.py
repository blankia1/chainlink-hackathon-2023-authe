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
    DYNAMO_DB_TABLE_NAME = os.environ['PermissionDocumentsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    if 'multiValueQueryStringParameters' in event:
        addresses =  event['multiValueQueryStringParameters'].get('address')
        version =  event['queryStringParameters'].get('version', 'ALL')
    else:
        addresses = event['address']
        version =  event.get('version', 'ALL')

    LOGGER.info(addresses)
    LOGGER.info("Addresses given are: {}".format(' '.join(map(str, addresses))))

    search_for_items = []
    found_items = []
    # Query items for only PK the permission documents from Dynamodb table
    if version == 'ALL':
        for address in addresses:
            # search_for_items.append({"address": {"S": address.lower() }})

            try:
                response = client.query(
                    TableName=DYNAMO_DB_TABLE_NAME,
                    KeyConditionExpression='address = :address',
                    ExpressionAttributeValues={
                        ':address': {"S": address.lower()}
                    }
                )
                found_items += response['Items']
            except Exception as err:
                LOGGER.error('Error retrieving the permission documents: %s' % err)
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        "message": "error",
                        "reason": err.args[0],
                        "detailed_reason": err.args[1:]
                }),
            } 
    else:
        for address in addresses:
            search_for_items.append({"address": {"S": address.lower() }, "version": {"S": version}})
        
        # Batch item Get the permission documents from Dynamodb table
        LOGGER.info("Retrieving the permission documents")
        try:
            response = client.batch_get_item(
                RequestItems={
                    DYNAMO_DB_TABLE_NAME: {
                        'Keys': search_for_items,
                        'ConsistentRead': True
                    }
                }
            )
        except Exception as err:
            LOGGER.error('Error retrieving the permission documents: %s' % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": err.args[0],
                    "detailed_reason": err.args[1:]
            }),
        } 

        found_items = response.get('Responses').get(DYNAMO_DB_TABLE_NAME)


    # Check if all permission documents have been found
    # No permission documents found at all
    LOGGER.info("Found number of permission documents: " + str(len(found_items)))
    
    parsed_items = []
    found_addresses = []
    for item in found_items:
        parsed_item = dynamo_obj_to_python_obj(item)
        parsed_items.append(parsed_item)
        # LOGGER.info(parsed_item)
        found_addresses.append(parsed_item.get('address'))

    # Check if all permission documents have been found for the addresses provided
    not_found_addresses = []
    for address in addresses:
        if address not in found_addresses: 
            not_found_addresses.append(address)

    if not_found_addresses != []:
        LOGGER.warning("No permission documents found for addresses: " + ' '.join(map(str, not_found_addresses)) + " and version: " + version)
    
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
    