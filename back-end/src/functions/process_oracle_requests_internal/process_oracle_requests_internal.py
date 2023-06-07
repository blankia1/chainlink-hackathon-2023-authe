import os
import json
import logging
import boto3
import requests
import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
import datetime

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    base_url = os.environ['BaseUrl']
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['TransactionsDynamoDBTableName']
    EVENTS_DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    timestamp = int(datetime.datetime.utcnow().timestamp())

    # Get the queue_messages
    if event.get('body'):
        queue_messages = json.loads(event['body'])
    else:
        queue_messages = event.get('Records')
        
    print(queue_messages)
    LOGGER.info("Got number of queue_messages: " + str(len(queue_messages)))

    for message in queue_messages:
        criticality_level = "5" # success
        queue_message = json.loads(message.get('body'))
        print(queue_message)
        
        status_code = queue_message.get('status_code')
        permission_documents = queue_message.get('permission_documents')
        request = queue_message['request']
        result = queue_message['result']
        error = queue_message['error']
        extra = queue_message['extra']
        
        if status_code == 200:
            print("no error")
            new_status = "approved"
            error_reason = ""
        else:
            print("error:", error)
            print("status_code", status_code)
            if status_code == 403:
                new_status = "denied"
                error_reason = error
                criticality_level = "2" # error
            else:
                new_status = "error"
                error_reason = error
                criticality_level = "2" # error
        
        encode_message_hash = extra.get('encode_message_hash', "")
        verified_encode_message_hash = extra.get('verified_encode_message_hash', "")

        from_address = request.get('f').lower()
        to_address = request.get('t').lower()
        function_name = request.get('n')
        encoded_data = request.get('d')
        resource_address = request.get('r').lower()
        
        result_message = result.get('message',"")
        permission_documents_from_address = permission_documents.get(from_address,"")
        permission_documents_resource_address = permission_documents.get(resource_address,"")

        obj1 = {
            "permission_document": permission_documents_from_address
        }
        dynamodb_permission_document_from_address_obj = python_obj_to_dynamo_obj(obj1).get('permission_document',"") 
     
        obj2 = {
            "permission_document": permission_documents_resource_address
        }
        dynamodb_permission_document_resource_address_obj = python_obj_to_dynamo_obj(obj2).get('permission_document',"") 
                
        LOGGER.info("Getting the last transaction from the DB for address: " + from_address )
        # Query transaction only by SK from Dynamodb table
        found_items = []
        try:
            response = client.query(
                TableName=DYNAMO_DB_TABLE_NAME,
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':address': {"S": from_address.lower()},
                    ':status': {"S": "approval_requested" },
                    ':encode_message_hash': {"S": encode_message_hash }, 
                    ':encoded_data': {"S": encoded_data },
                },
                IndexName='transactions-address-block-index',
                FilterExpression='#status = :status AND (contains(decoded_input_data, :encode_message_hash) OR contains(decoded_input_data, :encoded_data))',
                KeyConditionExpression='address = :address',
                ScanIndexForward=False,
            )
            found_items = response['Items']    
        except Exception as err:
            LOGGER.error('Error retrieving the transactions: %s' % err)
            raise Exception('Error retrieving the transactions: %s' % err)

        LOGGER.info("Found number of transactions: " + str(len(found_items)))
        LOGGER.info(found_items)

        # No transactions found at all
        if len(found_items) == 0:
            LOGGER.warning("No transactions for address: " + from_address)
            raise Exception('No transactions for address: %s' % from_address)
    
        parsed_item = dynamo_obj_to_python_obj(found_items[0])
    
        hash = parsed_item.get('hash')
        chain = parsed_item.get('chain')
        
        
        LOGGER.info("Write to DB")
        response = client.transact_write_items(
            TransactItems=[
                # Update is_confirmed to true
                {
                    'Update': {
                        'TableName': DYNAMO_DB_TABLE_NAME,
                        'Key': {
                            'hash': { 'S': hash }
                        },
                        'ConditionExpression': '#status = :status',
                        'UpdateExpression': 'SET #status = :new_status, resource_address = :resource_address, updated_at = :updated_at, result_message = :result_message, permission_documents_sender = :permission_documents_sender, permission_documents_resource_address = :permission_documents_resource_address, transaction_encoded_input_data = :transaction_encoded_input_data, encode_message_hash = :encode_message_hash, verified_encode_message_hash = :verified_encode_message_hash, error_reason = :error_reason ',
                        'ExpressionAttributeValues': {
                            ':status': { 'S': 'approval_requested'},
                            ':resource_address': { 'S': resource_address},
                            ':new_status': { 'S': new_status},
                            ':updated_at': {'N': str(timestamp)},
                            ':result_message': {'S': result_message},
                            ':permission_documents_sender': dynamodb_permission_document_from_address_obj,
                            ':permission_documents_resource_address': dynamodb_permission_document_resource_address_obj,
                            ':transaction_encoded_input_data': {'S': encoded_data},
                            ':encode_message_hash': {'S': encode_message_hash},
                            ':verified_encode_message_hash': {'S': verified_encode_message_hash}, 
                            ':error_reason': {'S': error_reason},
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
                                'address': { 'S': from_address },
                                'created_at': {'N': str(timestamp)},
                                'org': { 'S': 'default_org' },
                                'criticality_level': { 'S': criticality_level }, # 1. critical 2. error 3. warning 4. info .5 success
                                'chain': { 'S': chain },
                                'resource': { 'S': 'transactions' },
                                'message_summary': { 'S': 'More information has been added to your transaction' },
                                'message': { 'S': 'More information has been added to your transaction' },
                                'link_id': { 'S': hash },
                            }
                    }
                }
            ]
        )
   
    LOGGER.info("Finished")
   
    return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "success"
        }),
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
    