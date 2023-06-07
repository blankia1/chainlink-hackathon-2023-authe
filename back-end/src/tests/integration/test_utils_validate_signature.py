import pytest
import os
import sys
import json
import logging
import boto3
import moto
import requests
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

@pytest.fixture()
def test_env_params():
    """Load environment variables"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

good_payload = {
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

bad_payload = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "published",
    "chain": "sepolia",
    "signature": "0xd8ae60be06ff972296fd24865c3734a5f4d71ad0dcec539c09a6bedb284dc07e0a4f73b226d23a62e0b1d8f0cb251964ea440ec0bb0acd19f33374afd7f789cb1222c", # wrong signature
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
        "Signature": "0xd8ae60be06ff972296fd24865c3734a5f4d71ad0dcec539c09a6bedb284dc07e0a4f73b226d23a62e0b1d8f0cb251964ea440ec0bb0acd19f33374afd7f789cb1c"
    }
}

def test_utils_validate_signature(test_env_params):
    base_url = os.environ['BaseUrl']
    address = "0x560ecf1541389d71484374cfeb750847525582be"

    # Testing the Lambda
    LOGGER.info('Testing the utils validate signature Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/utils/validate-signature', json=good_payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from utils validate signature Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    
    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200    
    assert(result.get('message')) == 'success'    


def test_fail_on_address_utils_validate_signature(test_env_params):
    base_url = os.environ['BaseUrl']
    payload = good_payload
    payload['address'] = "FAKE_ADDRESS"

    # Testing the Lambda
    LOGGER.info('Testing the utils validate signature Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/utils/validate-signature', json=payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from utils validate signature Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    
    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 500    
    assert(result.get('reason')) == 'Error provided address is not valid'  


def test_fail_on_payload_utils_validate_signature(test_env_params):
    base_url = os.environ['BaseUrl']
    payload = bad_payload
    payload['address'] = "0x560ecf1541389d71484374cfeb750847525582be"

    # Testing the Lambda
    LOGGER.info('Testing the utils validate signature Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/utils/validate-signature', json=payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from utils validate signature Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    
    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 500    
    assert(result.get('reason')) == 'Signatures are not the same'