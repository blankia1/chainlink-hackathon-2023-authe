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
    "oracle_decoded_request": {
        "f": "fromaddress",
        "t": "to",
        "n": "transfer",
        "d": "['0x1234567890123456789012345678901234567890', _value: '0x1234567890123456789012345678901234567890']",
        "r": "resource_address"
    },
        "permission_documents": {
        "fromaddress": {
            "Version": "2023-05-11",
            "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:LINK:transfer"
                    ],
                    "Principal": [
                        "*"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Sid": "TestPermission2",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:ETH:transfer"
                    ],
                    "Principal": [
                        "*",
                        "0x1234567890123456789012345678901234567890"
                    ],
                    "Resource": [
                        "*",
                        "0x1234567890123456789012345678901234567890"
                    ]
                }
            ]
        },
        "resource_address": {
            "Version": "2023-05-11",
            "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
            "Statement": [
                {
                    "Sid": "DefaultResourcePermissions",
                    "Effect": "Allow",
                    "Action": [
                        "*"
                    ],
                    "Principal": [
                        "*"
                    ],
                    "Resource": [
                        "*"
                    ]
                }
            ]
        }
    }
}

def test_validate_transaction(test_env_params):
    base_url = os.environ['BaseUrl']

    # Testing the validate permission documents Lambda
    LOGGER.info('Testing the get permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/transactions/validate', json=good_payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from validate transaction Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200    
    assert(result.get('message')) == 'success'    

