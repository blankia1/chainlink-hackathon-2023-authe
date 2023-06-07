import os
import json
import logging
from web3 import Web3
from web3.auto import w3
from hexbytes import HexBytes
from eth_account.messages import encode_defunct

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):    
    # Get the permission document from the body
    if event.get('body'):
        permission_document = json.loads(event['body'])
    else:
        permission_document = event['permission_document']

    provided_signer_address = permission_document.get('address').lower()

    # get signature from permission document and from the statement
    extended_permission_document_provided_signature = permission_document.get('signature')
    permission_document_statement_provided_signature = permission_document.get('permission_document').get('Signature')

    # Create the new permission document statement without the signature. // Without the signature
    new_permission_document = {
        "Version": permission_document.get('permission_document').get('Version'),
        "Statement": permission_document.get('permission_document').get('Statement')
    }

    try:
        LOGGER.info("Signer Address provided is: " + provided_signer_address)
        LOGGER.info("The signatures provided: " + extended_permission_document_provided_signature + " and: " + permission_document_statement_provided_signature)
        # Check if the signature are both set and the same
        LOGGER.info("Verifying if all signatures are provided")
        if extended_permission_document_provided_signature != permission_document_statement_provided_signature:
            LOGGER.info("signature not the same: " + "extended_permission_document_provided_signature: " + extended_permission_document_provided_signature +  " permission_document_statement_provided_signature: " + permission_document_statement_provided_signature)
            raise Exception("Signatures are not the same") 

        # Check if address is a valid eth address
        LOGGER.info("Verifying if signer address provided is a valid eth address")
        if not Web3.is_address(provided_signer_address):
            LOGGER.error("Error provided address is not valid: " + " provided signer_address: " + provided_signer_address + " provided_signature: " + permission_document_statement_provided_signature + " permission_document: " + str(permission_document))
            raise Exception("Error provided address is not valid")
    
        # Verify the signature
        LOGGER.info("Verifying the address who signed the message:")
        w3 = Web3(Web3.HTTPProvider(""))

        provided_message = json.dumps(new_permission_document, indent=2)
        print(provided_message)

        mesage=encode_defunct(text=provided_message)
        message_signer_address = w3.eth.account.recover_message(mesage,signature=HexBytes(extended_permission_document_provided_signature))
        message_signer_address = message_signer_address.lower()
        LOGGER.info("Message has been signed by address: " + message_signer_address)
        
        # verify if its signed by the address owner
        if provided_signer_address != message_signer_address: 
            LOGGER.info("permission document not signed by address " + provided_signer_address + " vs: " +  message_signer_address + " message: " + provided_message)
            raise Exception("Permission document not signed by address")

        LOGGER.info("All good")
    except Exception as err:
        LOGGER.error(err)
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": str(err),
                # "detailed_reason": err[1:]
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
        }  
    
    return {
        'statusCode': 200,
        'body': json.dumps({"message":"success"}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
