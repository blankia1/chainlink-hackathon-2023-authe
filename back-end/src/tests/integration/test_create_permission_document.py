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

payload = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "draft",
    "chain": "sepolia",
    "signature": "0x924c7f89ea608408424db36ab8460801f700f276c3209d4d91f9c3602cf6ee5b5523a1e3b6263190e92ddad1e2521078008937239d76a165a3afc41777353f9c1c",
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
                    "*"
                ],
                "Principal": [
                    "*"
                ],
                "Sid": "AllowPermissions"
            }
        ],
        "Signature": "0x924c7f89ea608408424db36ab8460801f700f276c3209d4d91f9c3602cf6ee5b5523a1e3b6263190e92ddad1e2521078008937239d76a165a3afc41777353f9c1c"
    }
}

def test_create_permission_document(test_env_params):
    base_url = os.environ['BaseUrl']

    # Testing the create permission document Lambda
    LOGGER.info('Testing the create permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents', json=payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from create permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('id')) != None

