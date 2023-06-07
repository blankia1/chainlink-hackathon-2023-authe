import os
import json
import logging
import requests
import boto3
import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.dynamodb.conditions import Attr
import uuid
import datetime

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    region = os.environ['Region']
    base_url = os.environ['BaseUrl']
    DYNAMO_DB_TABLE_NAME = os.environ['DisputesDynamoDBTableName']
    EVENTS_DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    if 'pathParameters' in event:
        id = event['pathParameters']['id']
    else:
        id = event['id']

    # Get the dispute from the body
    if event.get('body'):
        dispute = json.loads(event['body'])
    else:
        dispute = event['dispute']

    # Generate the timestamp
    timestamp = int(datetime.datetime.utcnow().timestamp())

    LOGGER.info("dispute: " + str(dispute))

    # if status is 'draft' or 'rejected' then just update the item and return
    if dispute['status'] == 'published' or dispute['status'] == 'draft' or dispute['status'] == 'rejected':
        LOGGER.info("Published/Draft/Rejected flow")
        try:
            LOGGER.info("Inserting the new dispute into the db")
            response = client.transact_write_items(
                TransactItems=[
                    {
                        'Update': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Key': {
                                'id': { 'S': id },
                                'created_at': { 'N': dispute['created_at'] },
                            },
                            'ConditionExpression': '#status <> :status_published',
                            'UpdateExpression': 'SET #status = :new_status, chain = :chain, notes = :notes, updated_at = :updated_at',
                            'ExpressionAttributeValues': {
                                ':status_published': { 'S': 'published' },
                                ':new_status': { 'S': dispute['status'] },
                                ':chain': { 'S': dispute['chain'] },
                                ':notes': { 'S': dispute['notes'] },
                                ':updated_at': {'N': str(timestamp)},
                            },
                            'ExpressionAttributeNames':{
                                '#status': 'status'
                            },
                        }
                    },
                    # Create a record in the events table
                    {
                        'Put': {
                            'TableName': EVENTS_DYNAMO_DB_TABLE_NAME,
                            'Item': {
                                'address': { 'S': dispute['created_by'].lower()},
                                'created_at': {'N': str(timestamp)},
                                'org': { 'S': 'default_org' },
                                'criticality_level': { 'S': '4' }, # 1. critical 2. error 3. warning 4. info .5 success
                                'chain': { 'S': dispute['chain'] },
                                'resource': { 'S': 'disputes' },
                                'message_summary': { 'S': str(dispute['status']).capitalize() + ' - Dispute updated' },
                                'message': { 'S': 'A new dispute has been updated with the status: ' + dispute['status'] },
                                'link_id': { 'S': dispute['id'] }, # Match id of dispute
                            }
                        }
                    }
                ]
            )
            LOGGER.info("Finished Inserting the new dispute into the db")
        except Exception as err:
            LOGGER.info("Error can not update dispute with status is published")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "statusCode": 500,
                    "message": [
                        "Cannot update dispute with status published",
                    ],
                    "error": "Bad Request"
                }),
            } 

            LOGGER.info("Unexpected error: %s" % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": "Unexpected error",
                    "detailed_reason": str(err)
                })
            }
    else:
        LOGGER.info("Error Status unknown")
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": "Status unknown error",
            })
        }

    # return 200   
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success", "id": id}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },   
    } 

def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  

