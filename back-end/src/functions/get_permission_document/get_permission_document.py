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

    if 'pathParameters' in event:
        id =  event['pathParameters'].get('id')
    else:
        id = event['id']

    if 'queryStringParameters' in event and event.get('queryStringParameters') != None:
        format_permission_document_fe =  event['queryStringParameters'].get('format_permission_document_fe')
    else:
        format_permission_document_fe = event.get('format_permission_document_fe')

    LOGGER.info("id given is:" +  id)
    LOGGER.info("format_permission_document_fe given is:" + str(format_permission_document_fe))

    # Query item for only PK the permission documents from Dynamodb table
    try:
        response = client.query(
            TableName=DYNAMO_DB_TABLE_NAME,
            ExpressionAttributeValues={
                ':id': {"S": id}
            },
            IndexName='permission-documents-id-index',
            KeyConditionExpression='id = :id'
        )
    except Exception as err:
        LOGGER.error('Error retrieving the permission document: %s' % err)
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
        }),
    } 

    found_item = response['Items']

    # No permission documents found at all
    LOGGER.info("Found number of permission documents: " + str(len(found_item)))
    if len(found_item) == 0:
        LOGGER.warning("No permission documents found for id: " + id)
        return {
                'statusCode': 404,
                'body': json.dumps({
                    "message": "not_found",
                    "reason": "No permission documents found",
                    "detailed_reason": "No permission documents found for id: " + id
            }),
        } 

    parsed_item = dynamo_obj_to_python_obj(found_item[0])

    # A hack for the FE
    if format_permission_document_fe != None:
        parsed_item['permission_document'] = json.dumps(parsed_item['permission_document'])

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
    