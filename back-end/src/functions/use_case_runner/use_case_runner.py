import os
import json
import logging
import time
import boto3
import traceback
import requests
from datetime import datetime, date

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    if 'queryStringParameters' in event:
        _from =  event['queryStringParameters'].get('f').lower() 
        _to =  event['queryStringParameters'].get('t').lower() 
        _function_name =  event['queryStringParameters'].get('n')
        _data =  event['queryStringParameters'].get('d')
        _resource_address = event['queryStringParameters'].get('r', "default_resource_address").lower() 
    else:
        _from = event['f'].lower() 
        _to =  event['t'].lower() 
        _function_name =  event['n']
        _data =  event['d']
        _resource_address = event.get('r', "default_resource_address").lower() 
             
    obj = {
        'f' : _from,
        't' : _to,
        'n' : _function_name,
        'd' : _data,
        'r' : _resource_address
    } 
    
    LOGGER.info("Received the following oracle request: " + str(obj))

    base_url = os.environ['BaseUrl']


    # Decode the Oracle request
    LOGGER.info('Decoding the Oracle request')
    try:
        decoded_oracle_response = requests.post(base_url + '/public/ANY/v0/utils/decode', json = obj)
        decoded_oracle_result = decoded_oracle_response.json()
        if decoded_oracle_response.status_code != 200:
            raise Exception("Error decoding the Oracle request", obj, decoded_oracle_result)  
        LOGGER.info("decoded_oracle_result: " + str(decoded_oracle_result))
    except Exception as err:
        LOGGER.error(err)
        sendMessageToSqs(500, {}, obj, {}, err, {})
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        } 

    # Get the permission documents
    LOGGER.info('Getting the permission documents')
    addresses=[_from, _resource_address]
    try:
        permission_documents_resp = requests.get(base_url + '/public/GET/v0/permission-documents', params={'address': addresses, 'version' : 'LATEST'})
        permission_documents_result = permission_documents_resp.json()
        
        if permission_documents_resp.status_code != 200:
            LOGGER.info("Error getting the permission documents: " + permission_documents_result)
            raise Exception("Error getting the permission documents", "Error for addresses: " + ','.join(addresses), permission_documents_result)   

        # found_permission_documents = permission_documents_result.get('found_permission_documents')
        # not_found_permission_documents = permission_documents_result.get('not_found_permission_documents')
        found_permission_documents = permission_documents_result
        
        if permission_documents_resp.status_code == 200 and len(permission_documents_result) == []:
            LOGGER.info("No permission documents found for ALL addresses " + "Error for addresses: " + ','.join(addresses))
            raise Exception("No permission documents found for ALL addresses", "Error for addresses: " + ','.join(addresses), permission_documents_result)

        from_permission_document = None
        resource_permission_document = None
        for permission_document in found_permission_documents:
            if permission_document.get('address') == _from:
                from_permission_document = permission_document.get('permission_document')
            if permission_document.get('address') == _resource_address: 
                resource_permission_document = permission_document.get('permission_document')

        if permission_documents_resp.status_code == 200 and from_permission_document == None:
            LOGGER.error("Error no permission documents found for from address" + "Error for address: " + _from)
            raise Exception("Error no permission documents found for from address", "Error for address: " + _from) 
        if permission_documents_resp.status_code == 200 and resource_permission_document == None:
            LOGGER.warning("Error no permission documents found for resource_address address" + "Error for address: " + _resource_address)
            LOGGER.warning("Setting the default resource permission document for the resource address")
            resource_permission_document = {
                "Version": "2023-05-11",
                "Statement": [
                    {
                        "Resource": [
                            "*"
                        ],
                        "Effect": "Allow",
                        "Action": [
                            "*"
                        ],
                        "Principal": [
                            "*"
                        ],
                        "Sid": "DefaultResourceAddressAllowALLPermissions"
                    }
                ],
                "Signature": "unsigned"
            }
            # raise Exception("Error no permission documents found for resource_address address", "Error for address: " + _resource_address) 
        LOGGER.info('Finished getting the permission documents')
    except Exception as err:
        LOGGER.error(err)
        sendMessageToSqs(500, {}, obj, {}, err, {})
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        } 

    permission_documents = {
        _from: from_permission_document,
        _resource_address: resource_permission_document
    }

    # Validate the permission documents
    LOGGER.info('Validating the permission documents')
    for permission_document in [from_permission_document, resource_permission_document]:
        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            validated_permission_documents_response = requests.post(base_url + '/public/ANY/v0/permission-documents/validate/', json = permission_document, headers=headers)
            if validated_permission_documents_response.status_code != 200:
                raise Exception("Error validating the permission documents", permission_document, validated_permission_documents_response.json())  
            LOGGER.info('Finished Validating the permission documents') 
        except Exception as err:
            LOGGER.error(err)
            sendMessageToSqs(500, permission_documents, obj, {}, err, {})
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": err.args[0],
                    "detailed_reason": err.args[1:]
                }),
            } 

    validate_request = {
        "oracle_decoded_request": decoded_oracle_result,
        "permission_documents": permission_documents
    }

    # Validate the transaction
    LOGGER.info('Validating the transaction')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        validated_transaction_response = requests.post(base_url + '/public/ANY/v0/transactions/validate/', json = validate_request, headers=headers)
        if validated_transaction_response.status_code != 200:
            if validated_transaction_response.status_code == 403 and (validated_transaction_response.json()).get('reason') == "App 403 Forbidden":
                raise Exception("App 403 Forbidden", "Forbidden validating the transaction", validate_request, validated_transaction_response.json())  
            else:
                raise Exception("Error validating the transaction", validate_request, validated_transaction_response.json())   
        LOGGER.info("Finished validating the transaction")
    except Exception as err:
        LOGGER.error(err)
        # Return 403 when the permission document denies the action, principal or resource. All else throw 500 error
        if err.args[0] == "App 403 Forbidden":
            sendMessageToSqs(403, permission_documents, obj, {}, err, {})
            return {
                'statusCode': 403,
                'body': json.dumps({
                    "message": "forbidden",
                    "reason": err.args[0],
                    "detailed_reason": err.args[1:]
                }),
            }  
        else:
            sendMessageToSqs(500, permission_documents, obj, {}, err, {})
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "message": "error",
                    "reason": err.args[0],
                    "detailed_reason": err.args[1:]
                }),
            } 
    

    # Encode the message
    LOGGER.info('Encoding the message')
    # TODO get the function name from the call data
    messages_to_encode = {"messages_to_encode": [{ "address": _from }, { "address": _resource_address }, { "string": _data }]}
    verify_messages_to_encode = {"messages_to_encode": [{ "string": from_permission_document.get('Signature') }]}

    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        encode_message_response = requests.post(base_url + '/public/ANY/v0/utils/encode', json = messages_to_encode, headers=headers)
        encode_message_result = encode_message_response.json()
        if encode_message_response.status_code != 200:
            raise Exception("Error encoding the messages", encode_message_response.json())   

        verified_encode_message_response = requests.post(base_url + '/public/ANY/v0/utils/encode', json = verify_messages_to_encode, headers=headers)
        verified_encode_message_result = verified_encode_message_response.json()
        if verified_encode_message_response.status_code != 200:
            raise Exception("Error encoding the verified messages", verified_encode_message_response.json())   
    except Exception as err:
        LOGGER.error(err)
        sendMessageToSqs(500, permission_documents, obj, {}, err, {})
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        } 

    encode_message_hash = encode_message_result.get('encoded_message')
    verified_encode_message_hash = verified_encode_message_result.get('encoded_message')
    # 'HASH-OF-SOME-INPUTS-HERE_', # Need to provide hash of certain information like function_abi_plus_input_params
    s = encode_message_hash + '_' + verified_encode_message_hash + '_'
    return_message_in_bytes = "".join("{:02x}".format(ord(c)) for c in s)
        
    json_data = {
        'message': '0x' + return_message_in_bytes,
        'f': _from,
        't': _to,
        'n': decoded_oracle_result.get('n'),
        'd': decoded_oracle_result.get('d'),
        'permission_documents': permission_documents
    }   

    sendMessageToSqs(200, permission_documents, obj, json_data, {}, {"encode_message_hash": encode_message_hash, "verified_encode_message_hash": verified_encode_message_hash})

    LOGGER.info("Finished! Returning the following values:")
    LOGGER.info(str(json_data))

    return {
        'statusCode': 200,
        'body': json.dumps(json_data),
    }


def sendMessageToSqs(_status_code, _permission_documents, _request, _result, _error, _extra):
    LOGGER.info("Sending message to the queue")
    QueueUrl = os.environ['OracleRequestQueueUrl']
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S %p")

    obj = {
        "status_code": _status_code,
        "permission_documents": _permission_documents,
        "request": _request,
        "result": _result,
        "error": str(_error),
        "extra": _extra,
    }
    
    LOGGER.info("writing the following to the queue:")
    LOGGER.info(obj)
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=QueueUrl,
        MessageBody=json.dumps(obj)
    )

    LOGGER.info("Finished Sending message to the queue")
    return
    