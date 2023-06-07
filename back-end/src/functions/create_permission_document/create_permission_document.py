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
    DYNAMO_DB_TABLE_NAME = os.environ['PermissionDocumentsDynamoDBTableName']
    EVENTS_DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']

    client = boto3.client('dynamodb', region)

    # Get the extended permission document from the body
    if event.get('body'):
        extended_permission_document = json.loads(event['body'])
    else:
        extended_permission_document = event['extended_permission_document']

    # if 'queryStringParameters' in event and event.get('queryStringParameters') != None:
    #     format_permission_document_fe =  event['queryStringParameters'].get('format_permission_document_fe')
    # else:
    #     format_permission_document_fe = event.get('format_permission_document_fe')

    LOGGER.info("extended_permission_document: " + str(extended_permission_document))
    # LOGGER.info("format_permission_document_fe given is:" + str(format_permission_document_fe))

    # # A hack for the FE
    # if format_permission_document_fe != None:
    #     extended_permission_document['permission_document'] = json.loads(extended_permission_document['permission_document'])

    address = extended_permission_document.get('address').lower() 
    status = extended_permission_document.get('status')
    version = extended_permission_document.get('version')
    signature = extended_permission_document.get('signature')
    chain = extended_permission_document.get('chain')

    new_permission_document = extended_permission_document.get('permission_document')

    # Generate the unique id and timestamp
    id = uuid.uuid4().hex
    timestamp = int(datetime.datetime.utcnow().timestamp())

    # Validate the signature
    # Get the new signature and verify if its signed by the address owner
    signature_verified = False
    if signature == None or signature.startswith("0x") or status == "published":
        LOGGER.info('Validating the signature')
        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            validate_signature_response = requests.post(base_url + '/public/ANY/v0/utils/validate-signature', json = extended_permission_document, headers=headers)
            validate_signature_result = validate_signature_response.json()
            LOGGER.info(validate_signature_result)
            if validate_signature_response.status_code != 200:
                raise Exception("Error validating the signature", validate_signature_result)   
            signature_verified = True
        except Exception as err:
            LOGGER.error('Error validating the signature')
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "statusCode": 500,
                    "message": [
                        "Signature is not matching",
                        " Please sign the document again",
                    ],
                    "error": "Bad Request"
                }),
            } 
            
    if status == "draft":   # flow for insert draft item
        LOGGER.info("Flow for draft permission document")
        version = "draft_" + id # to guarantee uniqueness

        if signature == None:
            new_signature = "SIGNATURE_WILL_BE_ADDED_HERE" # insert dummy signature
        else:
            new_signature = signature

        LOGGER.info("address: " + address)
        LOGGER.info("id: " + id)
        LOGGER.info("version: " + "draft_" + id)
        LOGGER.info("status: " + status)
        LOGGER.info("signature: " + new_signature)
        LOGGER.info("chain: " + chain)
        LOGGER.info("new_permission_document: " + str(new_permission_document))

        obj = {
            'address': address,
            'version': version,
            'id': id,
            'status': status,
            'signature': new_signature,
            'chain': chain,
            "permission_document": new_permission_document
        }
        dynamodb_permission_document_obj = python_obj_to_dynamo_obj(obj).get('permission_document') 

        try:
            # table = boto3.resource("dynamodb", region).Table(DYNAMO_DB_TABLE_NAME)
            # table.put_item(Item=obj)

            response = client.transact_write_items(
                TransactItems=[
                    # Insert the permission document
                    {
                        'Put': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'version': { 'S': version },
                                    'id': { 'S': id },
                                    'chain': { 'S': chain },
                                    'signature': { 'S': new_signature },
                                    'status': { 'S': status },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                        }
                    },
                    # Create a record in the events table
                    {
                        'Put': {
                                'TableName': EVENTS_DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'created_at': {'N': str(timestamp)},
                                    'org': { 'S': 'default_org' },
                                    'criticality_level': { 'S': '4' }, # 1. critical 2. error 3. warning 4. info .5 success
                                    'chain': { 'S': chain },
                                    'resource': { 'S': 'permission-documents' },
                                    'message_summary': { 'S': str(status).capitalize() + ' - Permission document created' },
                                    'message': { 'S': 'A new permission document has been created with the status: ' + status },
                                    'link_id': { 'S': id }, # Match version of PD
                                }
                        }
                    }
                ]
            )
            LOGGER.info("Finished Inserting the new permission document into the db")
        except Exception as err:
            LOGGER.info("Unexpected error: %s" % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": "Unexpected error",
                    "detailed_reason": str(err)
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            }
    elif status == "published":
        LOGGER.info("Flow for publish permission document")

        if signature_verified == False or signature == None or signature == 'undefined' or signature == 'unsigned' or signature == "SIGNATURE_WILL_BE_ADDED_HERE":
            raise Exception("Signature needs to be set for published documents") 

        version = "LATEST"
        new_signature = signature

        # Validate the signature of the permission document
        try:
            # Verify the signature
            if new_signature == None:
                raise Exception("You need to add a signature")   

            validated_permission_document_signature = validate_signature(new_permission_document, new_signature) # raises error
        except Exception as err:
            LOGGER.info("Unexpected error: %s" % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": "Please sign the permission document again. Signature is invalid",
                    "detailed_reason": err.args[0:]
                }),
            }

        LOGGER.info("address: " + address)
        LOGGER.info("id: " + id)
        LOGGER.info("version: " + version + " and v1")
        LOGGER.info("status: " + status)
        LOGGER.info("signature: " + new_signature)
        LOGGER.info("chain: " + chain)
        LOGGER.info("new_permission_document: " + str(new_permission_document))

        # Find the latest existing version of the permission document
        response = client.batch_get_item(
            RequestItems={
                DYNAMO_DB_TABLE_NAME: {
                    'Keys': [{
                        'address': { 'S': address },
                        'version': { 'S': 'LATEST' }
                    }],
                    'ConsistentRead': True
                }
            }
        )

        found_items = response.get('Responses').get(DYNAMO_DB_TABLE_NAME)

        LOGGER.info("Found number of items: " + str(len(found_items)))

        obj = {
            "permission_document": new_permission_document
        }
        dynamodb_permission_document_obj = python_obj_to_dynamo_obj(obj).get('permission_document') 

        try:
            if found_items == []: # flow for no LATEST version yet
                LOGGER.info("Insert the new permission document with version 0")
                response = client.transact_write_items(
                    TransactItems=[
                        {
                            'Put': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'v1' },
                                    'id': { 'S': id },
                                    'status': { 'S': status },
                                    'signature': { 'S': new_signature },
                                    'chain': { 'S': chain },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                                'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)'
                            }
                        },
                        # Insert the LATEST version of the permission document with the new permission document info and version_ref
                        {
                            'Put': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'LATEST' },
                                    'version_ref': {'N': '1'},
                                    'id': { 'S': id + "_LATEST" },
                                    'status': { 'S': status }, 
                                    'signature': { 'S': new_signature },
                                    'chain': { 'S': chain },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                                'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)'
                            }
                        },
                        # Create a record in the events table
                        {
                            'Put': {
                                    'TableName': EVENTS_DYNAMO_DB_TABLE_NAME,
                                    'Item': {
                                        'address': { 'S': address },
                                        'created_at': {'N': str(timestamp)},
                                        'org': { 'S': 'default_org' },
                                        'criticality_level': { 'S': '5' }, # 1. critical 2. error 3. warning 4. info .5 success
                                        'chain': { 'S': chain },
                                        'resource': { 'S': 'permission-documents' },
                                        'message_summary': { 'S': str(status).capitalize() + ' - Permission document created' },
                                        'message': { 'S': 'A new permission document has been published' },
                                        'link_id': { 'S': id },
                                    }
                            }
                        }
                    ]
                )
            else: # Flow for LATEST version already exists so increment it

                LOGGER.info("LATEST version already exists: " + str(len(found_items)))

                latest_item = None
                for found_item in found_items:
                    local_parsed_item = dynamo_obj_to_python_obj(found_item) 
                    if local_parsed_item.get('version') == 'LATEST': 
                        latest_item = found_item
      
                if latest_item != None:
                    use_item = latest_item

                parsed_item = dynamo_obj_to_python_obj(use_item) 

                old_version_ref = str(parsed_item['version_ref'])
                new_version = str(int(old_version_ref)+1)
                old_permission_document = parsed_item['permission_document']
                old_signature_hash = parsed_item['signature']

                # Put the permission document if not exists yet
                # Need to compare signature data to not keeping on increasing versions
                response = client.transact_write_items(
                    TransactItems=[
                        {
                            'Put': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'v' + new_version },
                                    'id': { 'S': id },
                                    'status': { 'S': status },
                                    'chain': { 'S': chain },
                                    'signature': { 'S': new_signature },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                                'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)'
                            }
                        },       
                        # Update the LATEST version of the permission document with the new permission document info and version_ref
                        {
                            'Update': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Key': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'LATEST' }
                                },
                                'ConditionExpression': '#version_ref = :old_version_ref',
                                'UpdateExpression': 'SET version_ref = version_ref + :incr, id = :id, signature = :signature, permission_document = :permission_document, chain = :chain, updated_at = :updated_at',
                                'ExpressionAttributeValues': {
                                    ':incr': { 'N': '1' },
                                    ':old_version_ref': { 'N': old_version_ref },
                                    ':signature': { 'S': new_signature },
                                    ':permission_document': dynamodb_permission_document_obj,
                                    ':id': { 'S': id + "_LATEST"},
                                    ':chain': { 'S': chain },
                                    ':updated_at': {'N': str(timestamp)},
                                },
                                'ExpressionAttributeNames':{
                                    '#version_ref': 'version_ref'
                                },
                            }
                        },
                        # Update the previous LATEST version ref to new status 'overwritten'
                        {
                            'Update': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Key': {
                                    'address': { 'S': address },
                                    'version': { 'S': "v" + old_version_ref }
                                },
                                'ConditionExpression': '#status = :old_status',
                                'UpdateExpression': 'SET #status = :new_status, updated_at = :updated_at',
                                'ExpressionAttributeValues': {
                                    ':old_status': { 'S': 'published' },
                                    ':new_status': { 'S': 'overwritten' },
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
                                        'address': { 'S': address },
                                        'created_at': {'N': str(timestamp)},
                                        'org': { 'S': 'default_org' },
                                        'criticality_level': { 'S': '5' }, # 1. critical 2. error 3. warning 4. info .5 success
                                        'chain': { 'S': chain },
                                        'resource': { 'S': 'permission-documents' },
                                        'message_summary': { 'S': str(status).capitalize() + ' - Permission document created' },
                                        'message': { 'S': 'A new permission document has been published' },
                                        'link_id': { 'S': id },
                                    }
                            }
                        }
                    ]
                )
        except Exception as err:
            LOGGER.info("Unexpected error: %s" % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": "Unexpected error",
                    "detailed_reason": str(err)
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            }
    else:
        # status is not draft or publish
        LOGGER.info("Status is not draft or publish")
        return {
            'statusCode': 500,
            'body': json.dumps({"message": "Error - Status is not draft or published"}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
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

def validate_signature(permission_document, signature):
   return True
    
    
    