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
    DYNAMO_DB_TABLE_NAME = os.environ['PermissionDocumentsDynamoDBTableName']
    EVENTS_DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    if 'pathParameters' in event:
        id = event['pathParameters']['id']
    else:
        id = event['id']

    # Get the permission document from the body
    if event.get('body'):
        extended_permission_document = json.loads(event['body'])
    else:
        extended_permission_document = event['extended_permission_document']

    # Generate the timestamp
    timestamp = int(datetime.datetime.utcnow().timestamp())

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

    new_permission_document = extended_permission_document.get('permission_document') # needed for the FE

    # return {
    #     'statusCode': 400,
    #     'body': json.dumps({
    #         "statusCode": 400,
    #         "message": [
    #             "Signature is not matching",
    #             " Please sign the document again",
    #         ],
    #         "error": "Bad Request"
    #     }),
    #     'headers': {
    #         'Content-Type': 'application/json',
    #         'Access-Control-Allow-Origin': '*'
    #     },
    # }

    # Validate the signature
    # Get the new signature and verify if its signed by the address owner
    signature_verified = False
    if signature.startswith("0x") or status == "published":
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

    # if status is 'draft' or 'rejected' then just update the item and return
    if status == 'draft' or status == 'rejected':
        LOGGER.info("Draft flow")
        version = 'draft_' + id
        # version = id

        if signature == None or signature == 'undefined' or signature == 'unsigned':
            signature = "SIGNATURE_WILL_BE_ADDED_HERE" 

        # allign signature in extended with the one in permission document statement

        obj = {
            'address': address,
            'version': version,
            'status': status,
            'signature': signature,
            'chain': chain,
            "permission_document": new_permission_document
        }
        LOGGER.info("Address:" + address)
        LOGGER.info("Version:" + version)
        LOGGER.info("Status:" + status)
        LOGGER.info('Signature: ' + signature)
        LOGGER.info("Chain: " + chain)
        LOGGER.info("Permission_document: " + str(new_permission_document))

        obj = {
            "permission_document": new_permission_document
        }
        dynamodb_permission_document_obj = python_obj_to_dynamo_obj(obj).get('permission_document') 

        try:
            LOGGER.info("Inserting the new permission document into the db")
            # Update the permission document if exists
            # Need to compare signature data to not keeping on increasing versions
            response = client.transact_write_items(
                TransactItems=[
                    # Update the LATEST version of the permission document with the new permission document info and version_ref
                    {
                        'Update': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Key': {
                                'address': { 'S': address },
                                'version': { 'S': version }
                            },
                            'ConditionExpression': '#status = :old_status',
                            'UpdateExpression': 'SET permission_document = :permission_document, chain = :chain, #status = :new_status, signature = :signature, updated_at = :updated_at',
                            'ExpressionAttributeValues': {
                                ':old_status': { 'S': 'draft' },
                                ':new_status': { 'S': status },
                                ':chain': { 'S': chain },
                                ':signature': { 'S': signature },
                                ':permission_document': dynamodb_permission_document_obj,
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
                                    'criticality_level': { 'S': '4' }, # 1. critical 2. error 3. warning 4. info .5 success
                                    'chain': { 'S': chain },
                                    'resource': { 'S': 'permission-documents' },
                                    'message_summary': { 'S': str(status).capitalize() + ' - Permission document updated' },
                                    'message': { 'S': 'A new permission document has been created with the status: ' + status },
                                    'link_id': { 'S': id },
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
    elif (status == 'published'): #status is 'publish'
        LOGGER.info("Publish flow")
        # Generate a new unique id
        new_id = uuid.uuid4().hex

        if signature_verified == False or signature == None or signature == 'undefined' or signature == 'unsigned' or signature == "SIGNATURE_WILL_BE_ADDED_HERE":
            raise Exception("Signature needs to be set for published documents") 
            
        # Find the latest existing version of the permission document
        LOGGER.info("Find the latest permisison document and the draft + id one")
        response = client.batch_get_item(
            RequestItems={
                DYNAMO_DB_TABLE_NAME: {
                    'Keys': [{
                        'address': { 'S': address },
                        'version': { 'S': 'LATEST' }
                    },
                    {
                        'address': { 'S': address },
                        'version': { 'S': 'draft_' + id } # draft version of the document
                    },
                    ],
                    'ConsistentRead': True
                }
            }
        )

        found_items = response.get('Responses').get(DYNAMO_DB_TABLE_NAME)

        obj = {
            "permission_document": new_permission_document
        }
        dynamodb_permission_document_obj = python_obj_to_dynamo_obj(obj).get('permission_document') 

        try:
            LOGGER.info("found items is: " + str(len(found_items)))
            # Fail if not exists
            if found_items == 0:
                LOGGER.info("no items yet in Dynamodb for this address")
                raise Exception("no items yet in Dynamodb for this address. Use the POST method to insert new items") 
            
            latest_item = None
            draft_item = None
            for found_item in found_items:
                local_parsed_item = dynamo_obj_to_python_obj(found_item) 
                if local_parsed_item.get('version') == 'LATEST': 
                    latest_item = found_item
                if local_parsed_item.get('version') == ('draft_' + id): # draft version of the document
                    draft_item = found_item          

            if latest_item != None:
                LOGGER.info("Using the LATEST version")
                use_item = latest_item
            else:
                LOGGER.info("Using the DRAFT version")
                use_item = draft_item
            
            if draft_item:
                parsed_draft_item = dynamo_obj_to_python_obj(draft_item) # overwrite with the old retrieved draft version. Used for Idempotency
            else:
                parsed_draft_item = {}
                parsed_draft_item['status'] = "NO_DRAFT_PERMISSION_DOCUMENT_EXISTS" # Set a placeholder in case it doesnt exist

            parsed_item = dynamo_obj_to_python_obj(use_item) 

            if latest_item == None: # flow for first draft document to publish
                old_version_ref = str(0)     # When only 1 draft item exists and nothing else
                new_version = str(int(old_version_ref)+1)
                old_permission_document = parsed_item['permission_document']
                old_signature = parsed_item['signature']
                old_status = parsed_item['status']

                # Need to compare signature data to not keeping on increasing versions
                if old_status == status and (old_permission_document == str(new_permission_document) or old_signature == signature):
                    LOGGER.info("Permission document has not changed")
                    raise PermissionDocumentNotChangedException("Permission document has not changed", "New permission document: ",  
                        str(new_permission_document), "Old permission document: ", str(old_permission_document), 
                            "New signature:", signature, "Old signature:", old_signature )

                LOGGER.info("Creating a new permission document version")
                LOGGER.info("Address:" + address)
                LOGGER.info("New Signature:" + signature)
                LOGGER.info("Old Signature:" + old_signature)
                LOGGER.info('new_permission_document: ' +str(new_permission_document))
                LOGGER.info("new version: " + new_version)
                LOGGER.info("old version: " + old_version_ref)
                LOGGER.info("New status: " + status)
                LOGGER.info("Old status: " + old_status)

                LOGGER.info("Inserting the new permission document into the db")
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
                                    'id': { 'S': new_id },
                                    'chain': { 'S': chain },
                                    'signature': { 'S': signature },
                                    'status': { 'S': status },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                                'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)',
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
                                'UpdateExpression': 'SET version_ref = :version_ref, id = :id, signature = :signature, permission_document = :permission_document, chain = :chain, #status = :new_status, created_at = :created_at',
                                'ExpressionAttributeValues': {
                                    ':version_ref': { 'N': new_version },
                                    ':signature': { 'S': signature },
                                    ':permission_document': dynamodb_permission_document_obj,
                                    ':id': { 'S': new_id + "_LATEST"},
                                    ':chain': { 'S': chain },
                                    ':new_status': { 'S': status },
                                    ':created_at': {'N': str(timestamp)},
                                },
                                'ExpressionAttributeNames':{
                                    '#status': 'status'
                                },
                            }
                        },
                        # Delete the draft document
                        {
                            'Delete': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Key': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'draft_' + id }
                                }
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
                                    'message_summary': { 'S': str(status).capitalize() + ' - Permission document updated' },
                                    'message': { 'S': 'A new permission document has been published' },
                                    'link_id': { 'S': id },
                                }
                            }
                        }
                    ]
                )

            if latest_item != None: # flow for next publish document to new version
                old_version_ref = str(parsed_item['version_ref'])
                new_version = str(int(old_version_ref)+1)
                old_permission_document = parsed_item['permission_document']
                old_signature = parsed_item['signature']
                db_draft_status = parsed_draft_item['status']

                # Need to compare signature data to not keeping on increasing versions
                if db_draft_status == status and (old_permission_document == str(new_permission_document) or old_signature == signature):
                    LOGGER.info("Permission document has not changed")
                    raise PermissionDocumentNotChangedException("Permission document has not changed", "New permission document: ",  
                        str(new_permission_document), "Old permission document: ", str(old_permission_document), 
                            "New signature:", signature, "Old signature:", old_signature, "status:", status, "db_draft_status:", db_draft_status )

                LOGGER.info("Creating a new permission document version")
                LOGGER.info("Address:" + address)
                LOGGER.info("New Signature:" + signature)
                LOGGER.info("Old Signature:" + old_signature)
                LOGGER.info('new_permission_document: ' +str(new_permission_document))
                LOGGER.info("new version: " + new_version)
                LOGGER.info("old version: " + old_version_ref)
                LOGGER.info("New status: " + status)
                LOGGER.info("Old status: " + db_draft_status)
                
                # sanitized_id_for_latest = id if "_LATEST" in id else  id + "_LATEST"
                # sanitized_id_for_version = id.replace('_LATEST', '')
                # Put the permission document if not exists yet
                # Need to compare signature data to not keeping on increasing versions
                LOGGER.info("Inserting the new permission document into the db")
                response = client.transact_write_items(
                    TransactItems=[
                        {
                            'Put': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Item': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'v' + new_version },
                                    'id': { 'S': new_id },
                                    'chain': { 'S': chain },
                                    'signature': { 'S': signature },
                                    'status': { 'S': status },
                                    'permission_document': dynamodb_permission_document_obj,
                                    'created_at': {'N': str(timestamp)},
                                },
                                'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)',
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
                                'UpdateExpression': 'SET version_ref = version_ref + :incr, id = :id, signature = :signature, permission_document = :permission_document, chain = :chain, #status = :new_status, updated_at = :updated_at',
                                'ExpressionAttributeValues': {
                                    ':incr': { 'N': '1' },
                                    ':old_version_ref': { 'N': old_version_ref },
                                    ':signature': { 'S': signature },
                                    ':permission_document': dynamodb_permission_document_obj,
                                    ':id': { 'S': new_id + "_LATEST" },
                                    ':chain': { 'S': chain },
                                    ':new_status': { 'S': status },
                                    ':updated_at': {'N': str(timestamp)},
                                },
                                'ExpressionAttributeNames':{
                                    '#version_ref': 'version_ref',
                                    '#status': 'status'
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
                        # Delete the draft document
                        {
                            'Delete': {
                                'TableName': DYNAMO_DB_TABLE_NAME,
                                'Key': {
                                    'address': { 'S': address },
                                    'version': { 'S': 'draft_' + id }
                                }
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
                                    'message_summary': { 'S': str(status).capitalize() + ' - Permission document updated' },
                                    'message': { 'S': 'A new permission document has been published' },
                                    'link_id': { 'S': id },
                                }
                            }
                        }
                    ]
                )
        except botocore.exceptions.ParamValidationError as err:
            LOGGER.info("ParamValidationError Unexpected error: %s" % err)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": "Dynamodb ParamValidationError Unexpected error",
                    "detailed_reason": str(err)
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            }
        except PermissionDocumentNotChangedException as err:
            LOGGER.info("PermissionDocumentNotChangedException Unexpected error: %s" % err) 
        except Exception as err:
            LOGGER.error("Unexpected error: %s" % err)
            # if err.response['Error']['Code'] == 'TransactionCanceledException':
            #     LOGGER.error("Permission Document version already exists")
            #     LOGGER.error("Unexpected error: %s" % err)
            # else:
            #     LOGGER.error("Unexpected error: %s" % err)
            
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": err.response['Error']['Code'],
                    "detailed_reason": str(err)
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
            }

        # response = client.get_item(
        #     TableName = DYNAMO_DB_TABLE_NAME,
        #     Key = {
        #         'address': { 'S': address },
        #         'version': { 'S': 'LATEST' },
        #     }
        # )
        # parsed_item = dynamo_obj_to_python_obj(response['Item']) 
        # LOGGER.info(parsed_item)

        # response = client.scan(TableName = DYNAMO_DB_TABLE_NAME)
        # data = response['Items']

        # while 'LastEvaluatedKey' in response:
        #     response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        #     data.extend(response['Items'])

        # for item in data:
        #     parsed_item = dynamo_obj_to_python_obj(item) 
        #     LOGGER.info(parsed_item)

        return {
            'statusCode': 200,
            'body': json.dumps({"message": "success", "id": id}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }
    else:
        # Status not found. Not in published, draft, rejected
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "status not found"}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
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

class PermissionDocumentNotChangedException(Exception):
    pass
    