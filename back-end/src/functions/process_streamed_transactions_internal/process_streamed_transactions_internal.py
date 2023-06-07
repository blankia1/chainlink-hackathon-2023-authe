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
    print(event)
    base_url = os.environ['BaseUrl']
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['TransactionsDynamoDBTableName']
    EVENTS_DYNAMO_DB_TABLE_NAME = os.environ['EventsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    timestamp = int(datetime.datetime.utcnow().timestamp())

    # Get the queue_messages
    # print(event)
    if event.get('body'):
        queue_messages = json.loads(event['body'])
    else:
        queue_messages = event.get('Records')
        
    # print(queue_messages)
    for message in queue_messages:
        queue_message = json.loads(message.get('body'))
        print(queue_message)

        is_confirmed = queue_message['confirmed']
        chain = get_chain_name(queue_message['chainId'])
        stream_id = queue_message['streamId']
        tag = queue_message['tag']
        block = queue_message['block']
        block_number = block['number']
        transactions = queue_message['txs']

        LOGGER.info("Got number of transactions from Moralis: " + str(len(transactions)))
    
        dynamodb = boto3.resource('dynamodb',region_name=region)
    
        LOGGER.info("Is confirmed: " + str(is_confirmed))
        LOGGER.info("stream_id: " + stream_id)
        LOGGER.info("tag: " + tag)
    

        if len(transactions) > 0:
            LOGGER.info("Adding the transactions to the DB")
    
            for transaction in transactions:
                address = transaction['fromAddress'].lower() 
                to_address = transaction.get('toAddress').lower() 
                hash = transaction["hash"]
                input = transaction.get('input')
                receipt_status = transaction.get('receiptStatus')

                LOGGER.info("Adding the transaction to the DB")
                LOGGER.info("Address: " + address) 
                LOGGER.info("To Address: " + to_address) 
                LOGGER.info("Hash: " + hash) 
                LOGGER.info("Chain: " + chain) 
                LOGGER.info("Input: " + input) 
                LOGGER.info("receipt_status: " + receipt_status)
                
                # Decode the input data in the transaction
                LOGGER.info('Decoding the input data')
                obj = {
                    'f' : address,
                    't' : to_address,
                    'n' : "UNKNOWN",
                    'd' : input,
                    'r' : to_address
                } 
                try:
                    decoded_input_data_response = requests.post(base_url + '/public/ANY/v0/utils/decode', json = obj)
                    decoded_input_data_result = decoded_input_data_response.json()
                    if decoded_input_data_response.status_code != 200:
                        raise Exception("Error decoding the input data", obj, decoded_input_data_result)  
                    LOGGER.info('Finished decoding the input data')
                except Exception as err:
                    LOGGER.error("Unexpected error: %s" % err)
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            "message": "error",
                            "reason": err.args[0],
                            "detailed_reason": err.args[1:]
                        }),
                    }  

                decoded_input_data = decoded_input_data_result.get('d')
                decoded_input_function = decoded_input_data_result.get('n')
                LOGGER.info(decoded_input_data)
                LOGGER.info(decoded_input_function)


                try:
                    if tag == "AuthEProxy":
                        LOGGER.info("Queue message comming from AuthEProxy")
                        status = "approval_requested"
                        if is_confirmed == False: # the transaction is new and unconfirmed
                            LOGGER.info("Is confirmed is False")
                            criticality_level = "4" # info
                            response = client.transact_write_items(
                                TransactItems=[
                                    {
                                        'Put': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Item': {
                                                "address": { 'S': address },
                                                "to_address": { 'S': to_address },
                                                "hash": { 'S': hash },
                                                "org": { 'S':  "default_org" },
                                                "block_number": { 'S': block_number },
                                                "stream_id": { 'S': stream_id },
                                                "tag":  { 'S': tag },
                                                "block": { 'M':  python_obj_to_dynamo_obj(block)},
                                                "is_confirmed": { 'BOOL': is_confirmed },
                                                "chain": { 'S': chain },
                                                "encoded_data" : { 'S': input },
                                                "decoded_input_data": { 'S': str(decoded_input_data) },
                                                "decoded_input_function": { 'S': decoded_input_function },
                                                "transaction": { 'M': python_obj_to_dynamo_obj(transaction)}, 
                                                'created_at': {'N': str(timestamp)},
                                                'status': { 'S': status }
                                            },
                                            'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(#hash)',
                                            'ExpressionAttributeNames':{
                                                "#hash": "hash"
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
                                                    'criticality_level': { 'S': criticality_level }, # 1. critical 2. error 3. warning 4. info .5 success
                                                    'chain': { 'S': chain },
                                                    'resource': { 'S': 'transactions' },
                                                    'message_summary': { 'S': 'Unconfirmed transaction has been added' },
                                                    'message': { 'S': 'A new unconfirmed transaction has been seen on the blockchain' },
                                                    'link_id': { 'S': hash },
                                                }
                                        }
                                    }
                                ]
                            )
                            LOGGER.info("Finished writing to the DB")
                        else: # is_confirmed == true
                            LOGGER.info("Is confirmed is True")
                            criticality_level = "5" # success
                            response = client.transact_write_items(
                                TransactItems=[
                                    # Update is_confirmed to true
                                    {
                                        'Update': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Key': {
                                                'hash': { 'S': hash }
                                            },
                                            'ConditionExpression': 'attribute_exists(#hash) AND #is_confirmed <> :is_confirmed',
                                            'UpdateExpression': 'SET is_confirmed = :is_confirmed, updated_at = :updated_at',
                                            'ExpressionAttributeValues': {
                                                ':is_confirmed': { 'BOOL': is_confirmed },
                                                ':updated_at': {'N': str(timestamp)},
                                            },
                                            'ExpressionAttributeNames':{
                                                '#is_confirmed': 'is_confirmed',
                                                '#hash': 'hash'
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
                                                    'criticality_level': { 'S': criticality_level }, # 1. critical 2. error 3. warning 4. info .5 success
                                                    'chain': { 'S': chain },
                                                    'resource': { 'S': 'transactions' },
                                                    'message_summary': { 'S': 'Confirmed transaction has been added' },
                                                    'message': { 'S': 'A new confirmed transaction has been seen on the blockchain' },
                                                    'link_id': { 'S': hash },
                                                }
                                        }
                                    }
                                ]
                            )       
                            LOGGER.info("Finished writing to the DB")
                    elif tag == "CustomERC20":
                        LOGGER.info("Queue message comming from CustomERC20")
                        status = "success"
                        erc20_transfers = queue_message.get('erc20Transfers', [])
                        erc20_transfer_found = {}
                        erc20_to_address = to_address # default
                        for erc20_transfer in erc20_transfers:
                            transaction_hash = erc20_transfer.get('transactionHash')
                            erc20_transfer_found = erc20_transfer
                            erc20_to_address = erc20_transfer.get('to', to_address)
                                        
                        if is_confirmed == False: # the transaction is new and unconfirmed
                            LOGGER.info("Is confirmed is False")
                            criticality_level = "4" # info

                            LOGGER.info("Getting the last transaction approval from the DB for address: " + address + " and decoded_input_data: " + input)
                            # Get latest approval request
                            # Query transaction only by SK from Dynamodb table
                            found_items = []
                            try:
                                response_last_approval = client.query(
                                    TableName=DYNAMO_DB_TABLE_NAME,
                                    ExpressionAttributeNames={'#status': 'status'},
                                    ExpressionAttributeValues={
                                        ':address': {"S": address.lower()},
                                        ':status_approved':{"S":"approved"},
                                        ':status_approval_requested':{"S":"approval_requested"},
                                        ':decoded_input_data': {"S": input }, # Its a nested decoded obj in this one
                                    },
                                    IndexName='transactions-address-block-index',
                                    FilterExpression='(#status = :status_approved OR #status = :status_approval_requested) and contains(decoded_input_data, :decoded_input_data)',
                                    KeyConditionExpression='address = :address',
                                    ScanIndexForward=False,
                                )
                                found_items = response_last_approval['Items']     
                            except Exception as err:
                                LOGGER.error('Error retrieving the transactions: %s' % err)
                                raise Exception("Error retrieving the transactions")

                            LOGGER.info("Found number of transactions: " + str(len(found_items)))
                            LOGGER.info(found_items)
                            if len(found_items) > 0:
                                parsed_item = dynamo_obj_to_python_obj(found_items[0])
                                permission_documents_sender = parsed_item.get('permission_documents_sender')
                                permission_documents_resource_address = parsed_item.get('permission_documents_resource_address')
                                decoded_input_function = parsed_item.get('decoded_input_function')
                                linked_to_approval_hash = parsed_item.get('hash')
                            else:
                                permission_documents_sender = "UNKNOWN"
                                permission_documents_resource_address = "UNKNOWN"
                                decoded_input_function = "UNKNOWN"
                                linked_to_approval_hash = "UNKNOWN"
                                status = "not_authe_provider"
                                criticality_level = "3" # warning

                            obj1 = {
                                "permission_document": permission_documents_sender
                            }
                            dynamodb_permission_document_from_address_obj = python_obj_to_dynamo_obj(obj1).get('permission_document',"") 
                        
                            obj2 = {
                                "permission_document": permission_documents_resource_address
                            }
                            dynamodb_permission_document_resource_address_obj = python_obj_to_dynamo_obj(obj2).get('permission_document',"") 

                            LOGGER.info("Inserting into the DB")
                            response = client.transact_write_items(
                                TransactItems=[
                                    {
                                        'Put': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Item': {
                                                "address": { 'S': address },
                                                "to_address": { 'S': erc20_to_address },
                                                "resource_address": { 'S': obj.get('r') },
                                                "hash": { 'S': hash },
                                                "org": { 'S':  "default_org" },
                                                "block_number": { 'S': block_number },
                                                "stream_id": { 'S': stream_id },
                                                "tag":  { 'S': tag },
                                                "block": { 'M':  python_obj_to_dynamo_obj(block)},
                                                "is_confirmed": { 'BOOL': is_confirmed },
                                                "chain": { 'S': chain },
                                                "encoded_data" : { 'S': input },
                                                "decoded_input_data": { 'S': str(decoded_input_data) },
                                                "decoded_input_function": { 'S': decoded_input_function },
                                                "transaction": { 'M': python_obj_to_dynamo_obj(transaction)}, 
                                                "erc20_transfer": { 'M': python_obj_to_dynamo_obj(erc20_transfer_found)}, 
                                                'permission_documents_sender': dynamodb_permission_document_from_address_obj,
                                                'permission_documents_resource_address': dynamodb_permission_document_resource_address_obj,
                                                'created_at': {'N': str(timestamp)},
                                                'status': { 'S': status },
                                                'linked_to_approval': { 'S': linked_to_approval_hash }, 
                                            },
                                            'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(#hash)',
                                            'ExpressionAttributeNames':{
                                                "#hash": "hash"
                                            },
                                        }
                                    }, 
                                    # Update the status of the old approval record to show that you used the approval # if hash = UNKNOWN then it will update the placeholder
                                    {
                                        'Update': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Key': {
                                                'hash': { 'S': linked_to_approval_hash }
                                            },
                                            'UpdateExpression': 'SET #status = :status, updated_at = :updated_at',
                                            'ExpressionAttributeValues': {
                                                ':status': { 'S': 'approval_used_unconfirmed' },
                                                ':updated_at': {'N': str(timestamp)},
                                            },
                                            'ExpressionAttributeNames':{
                                                '#status': 'status',
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
                                                    'criticality_level': { 'S': criticality_level }, # 1. critical 2. error 3. warning 4. info .5 success
                                                    'chain': { 'S': chain },
                                                    'resource': { 'S': 'transactions' },
                                                    'message_summary': { 'S': 'Unconfirmed ERC20 transaction has been added' },
                                                    'message': { 'S': 'A new unconfirmed ERC20 transaction has been seen on the blockchain' },
                                                    'link_id': { 'S': hash },
                                                }
                                        }
                                    },                                
                                ]
                            )
                            LOGGER.info("Finished writing to the DB")
                        else: # is_confirmed == true
                            LOGGER.info("Is confirmed is True")
                            criticality_level = "5" # success

                            LOGGER.info("Getting the last transaction approval_used_unconfirmed from the DB for address: " + address + " and decoded_input_data: " + input)
                            # Get latest approval request
                            # Query transaction only by SK from Dynamodb table
                            found_items = []
                            try:
                                response_last_approval = client.query(
                                    TableName=DYNAMO_DB_TABLE_NAME,
                                    ExpressionAttributeNames={'#status': 'status'},
                                    ExpressionAttributeValues={
                                        ':address': {"S": address.lower()},
                                        ':status_approval_used_unconfirmed':{"S":"approval_used_unconfirmed"},
                                        ':decoded_input_data': {"S": input }, # Its a nested decoded obj in this one
                                    },
                                    IndexName='transactions-address-block-index',
                                    FilterExpression='#status = :status_approval_used_unconfirmed and contains(decoded_input_data, :decoded_input_data)',
                                    KeyConditionExpression='address = :address',
                                    ScanIndexForward=False,
                                )
                                found_items = response_last_approval['Items']     
                            except Exception as err:
                                LOGGER.error('Error retrieving the transactions: %s' % err)
                                raise Exception("Error retrieving the transactions")

                            LOGGER.info("Found number of transactions: " + str(len(found_items)))
                            LOGGER.info(found_items)
                            if len(found_items) > 0:
                                parsed_item = dynamo_obj_to_python_obj(found_items[0])
                                linked_to_approval_hash = parsed_item.get('hash')
                            else:
                                linked_to_approval_hash = "UNKNOWN"
                                status = "not_authe_provider"

                            LOGGER.info("Inserting into the DB")
                            response = client.transact_write_items(
                                TransactItems=[
                                    # Update is_confirmed to true
                                    {
                                        'Update': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Key': {
                                                'hash': { 'S': hash }
                                            },
                                            'ConditionExpression': 'attribute_exists(#hash) AND #is_confirmed <> :is_confirmed',
                                            'UpdateExpression': 'SET is_confirmed = :is_confirmed, updated_at = :updated_at',
                                            'ExpressionAttributeValues': {
                                                ':is_confirmed': { 'BOOL': is_confirmed },
                                                ':updated_at': {'N': str(timestamp)},
                                            },
                                            'ExpressionAttributeNames':{
                                                '#is_confirmed': 'is_confirmed',
                                                '#hash': 'hash'
                                            },
                                        }
                                    },
                                    # Update the status of the old approval record to show that you used the approval # if hash = UNKNOWN then it will update the placeholder
                                    {
                                        'Update': {
                                            'TableName': DYNAMO_DB_TABLE_NAME,
                                            'Key': {
                                                'hash': { 'S': linked_to_approval_hash }
                                            },
                                            'UpdateExpression': 'SET #status = :status, updated_at = :updated_at',
                                            'ExpressionAttributeValues': {
                                                ':status': { 'S': 'approval_used' },
                                                ':updated_at': {'N': str(timestamp)},
                                            },
                                            'ExpressionAttributeNames':{
                                                '#status': 'status',
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
                                                    'criticality_level': { 'S': criticality_level }, # 1. critical 2. error 3. warning 4. info .5 success
                                                    'chain': { 'S': chain },
                                                    'resource': { 'S': 'transactions' },
                                                    'message_summary': { 'S': 'Confirmed ERC20 transaction has been added' },
                                                    'message': { 'S': 'A new confirmed ERC20 transaction has been seen on the blockchain' },
                                                    'link_id': { 'S': hash },
                                                }
                                        }
                                    }
                                ]
                            )   
                            LOGGER.info("Finished writing to the DB")
                except botocore.exceptions.ClientError as err:
                    # Ignore the ConditionalCheckFailedException
                    if err.response['Error']['Code'] != 'ConditionalCheckFailedException':
                        LOGGER.warn("The transaction already exists in the DB: %s" % err)
                        raise Exception("Error ConditionalCheckFailedException writing the transaction to the DB %s" % err)
                except Exception as err:
                    LOGGER.error("Unexpected error: %s" % err)
                    raise Exception("Error writing the transaction to the DB %s" % err)

    LOGGER.info("Finished writing the transaction to the DB")
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success"}),

        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def get_chain_name(chain_id):
    match chain_id:
        case "0xaa36a7":
             return "sepolia"
        case _:
            raise Exception("Chain id is unknown")


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
    