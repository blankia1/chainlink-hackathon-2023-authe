import pytest
import os
import sys
import json
import logging

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.utils_validate_signature.utils_validate_signature import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

from_address = "0x560ecf1541389d71484374cfeb750847525582be"

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def test_utils_validate_signature_lambda_handler(test_env_params):
    event = { 
        "body": json.dumps(example_permission_document),
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    assert body["message"] == "success" 

def test_incorrect_signature_utils_validate_signature_lambda_handler(test_env_params):
    event = { 
        "body": json.dumps(incorrect_signature_permission_document),
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    assert body["reason"] == "Signatures are not the same"


def test_incorrect_signer_address_provided_utils_validate_signature_lambda_handler(test_env_params):
    from_address = "d3cda913deb6f67967b99d67acdfa1712c293601" # correct eth address, but is not signer
    example_permission_document['address'] = from_address
    event = { 
        "body": json.dumps(example_permission_document),
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    assert body["reason"] == "Permission document not signed by address"

def test_incorrect_eth_signer_address_provided_utils_validate_signature_lambda_handler(test_env_params):
    from_address = "eeeee" # incorrect eth address
    example_permission_document['address'] = from_address
    print(example_permission_document)
    event = { 
        "body": json.dumps(example_permission_document),
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    assert body["reason"] == "Error provided address is not valid"


def test_custom_utils_validate_signature_lambda_handler(test_env_params):
    event = { 
        "body": json.dumps(custom_correct_signature_permission_document),
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)


example_permission_document = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "published",
    "chain": "sepolia",
    "signature": "0xdf14a06e65ba7114e36f526ddfec5e52d43c481ef40eb625c56c41806197d6f457be75727778d72e18662eb7f0d80b99689c1ccb05f5be605173197e1dd2f0271c",
    "version": "unknown",
    "permission_document": {
        "Version": "2023-05-11",
        "Statement": [
            {
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Action": [
                "approve"
            ],
            "Principal": [
                "*"
            ],
            "Sid": "AllowPermissions"
            }
        ],
        "Signature": "0xdf14a06e65ba7114e36f526ddfec5e52d43c481ef40eb625c56c41806197d6f457be75727778d72e18662eb7f0d80b99689c1ccb05f5be605173197e1dd2f0271c"
    }
}

incorrect_signature_permission_document = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "published",
    "chain": "sepolia",
    "signature": "0xd8ae60be06ff972296fd24865c3734a5f4d71ad0dcec539c09a6bedb284dc07e0a4f73b226d23a62e0b1d8f0cb251964ea440ec0bb0acd19f33374afd7f789cb1c",
    "version": "unknown",
    "permission_document": {
        "Version": "2023-05-11",
        "Signature": "INCORRECT_SIGNATURE",
        "Statement": [
            {
                "Sid": "TestPermission",
                "Effect": "Allow",
                "Action": [
                    "erc20:LINK:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            },
            {
                "Sid": "TestPermission2",
                "Effect": "Allow",
                "Action": [
                    "erc20:ETH:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            }
        ]
    }
}

custom_correct_signature_permission_document = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "published",
    "chain": "sepolia",
    "signature": "0xbc5841c3124d6e5fdeb9f87bf34fb818323df532ce45f182fcd68af60f4ba6a443c5ca2bd164a0ab1887238e432f2ece62635df3049c0978fc8adfa8c19beab51c",
    "version": "unknown",
    "permission_document": {
        "Version": "2023-05-11",
        "Statement": [
            {
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Action": [
                "transfer"
            ],
            "Principal": [
                "*"
            ],
            "Sid": "AllowPermissions"
            }
        ],
        "Signature": "0xbc5841c3124d6e5fdeb9f87bf34fb818323df532ce45f182fcd68af60f4ba6a443c5ca2bd164a0ab1887238e432f2ece62635df3049c0978fc8adfa8c19beab51c"
    }
}