import os
import json
import logging
import requests
import boto3
import botocore
import uuid
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
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

    # Get the dispute from the body
    if event.get('body'):
        dispute = json.loads(event['body'])
    else:
        dispute = event['dispute']

    LOGGER.info("dispute: " + str(dispute))
    

    # Generate the unique id and timestamp
    id = uuid.uuid4().hex
    timestamp = int(datetime.datetime.utcnow().timestamp())
    dispute['id'] = id
    dispute['created_by'] = dispute['created_by'].lower() 

    if dispute['status'] == "published" or dispute['status'] == "draft" or dispute['status'] == "rejected":   # flow for insert published/draft/rejected item
        LOGGER.info("Flow for draft dispute")
        version = "draft_" + id # to guarantee uniqueness
        try:
            LOGGER.info("Putting the dispute in the DB")
            response = client.transact_write_items(
                TransactItems=[
                    # Insert the dispute
                    {
                        'Put': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Item': {
                                'created_by': { 'S': dispute['created_by'].lower() },
                                'resource_address': { 'S': dispute['resource_address'].lower() },
                                'transaction_hash': { 'S': dispute['transaction_hash'] },
                                'id': { 'S': id },
                                'org': { 'S': "default_org" },
                                'action': { 'S': dispute['action'] },
                                'chain': { 'S': dispute['chain'] },
                                'status': { 'S': dispute['status'] },
                                'created_at': {'N': str(timestamp)},
                                'contract_abi': {'S': str(dispute['contract_abi'])},
                                'function_abi': {'S': str(dispute['function_abi'])},
                                'permission_document': {'S': str(dispute['permission_document'])},
                                'encoded_input_data': {'S': str(dispute['transaction_encoded_input_data'])},
                                'decoded_input_data': {'S': str(dispute['decoded_input_data'])},
                                'result_hash': {'S': str(dispute['result_hash'])},
                                'proof_hash_result': {'S': str(dispute['proof_hash_result'])},
                                'notes': {'S': str(dispute['notes'])},
                                'linked_approval': {'S': str(dispute['linked_approval'])},
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
                                'criticality_level': { 'S': '5' }, # 1. critical 2. error 3. warning 4. info .5 success
                                'chain': { 'S': dispute['chain'] },
                                'resource': { 'S': 'disputes' },
                                'message_summary': { 'S': str(dispute['status']).capitalize() + ' - Dispute created' },
                                'message': { 'S': 'A new dispute has been created with the status: ' + dispute['status'] },
                                'link_id': { 'S': id }, # Match id of dispute
                            }
                        }
                    }
                ]
            )
            LOGGER.info("Finished Inserting the new dispute into the db")
        except Exception as err:
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
        
        