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
    "Version": "2023-05-11",
    "Signature": "3047a8ed3726b536ffdfa690e79bfecf2f9e942e4fcbb524898027b5",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": ["*"],
            "Resource": ["*"]
        }
    ]
}

bad_payload = {
    "Version": "2023-05-11",
    "Signature": "3047a8ed3726b536ffdfa690e79bfecf2f9e942e4fcbb524898027b5",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "FAKE_EFFECT_ADDED_HERE",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": ["*"],
            "Resource": ["*"]
        }
    ]
}

def test_validate_permission_documents(test_env_params):
    base_url = os.environ['BaseUrl']

    # Testing the validate permission documents Lambda
    LOGGER.info('Testing the get permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents/validate/', json=good_payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from validate permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200    
    assert(result.get('message')) == 'success'    

def test_fail_validate_permission_documents(test_env_params):
    base_url = os.environ['BaseUrl']

    # Testing the validate permission documents Lambda
    LOGGER.info('Testing the get permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents/validate/', json=bad_payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from validate permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 500    
    assert(result.get('message')) == 'error'   
    assert(result.get('reason')) == "Statement contains incorrect 'Effect'"   

