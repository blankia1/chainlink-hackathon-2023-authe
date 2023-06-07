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

payload = {
    "address": "0x560ecf1541389d71484374cfeb750847525582be",
    "status": "published",
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

@pytest.fixture()
def test_env_params():
    """Load environment variables"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def test_get_permission_document(test_env_params):
    base_url = os.environ['BaseUrl']
    addresses = ['0x560ecf1541389d71484374cfeb750847525582be']
    version = 'LATEST'

    # First insert a new one
    LOGGER.info('Testing the create permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents', json=payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from create permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    # Testing the get permission documents Lambda
    LOGGER.info('Testing the get permission documents Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/permission-documents', params={'address': addresses, 'version' : 'LATEST'}, headers=headers)
    result = response.json()

    assert(response.status_code) == 200 
    found_permission_documents = result

    assert(len(found_permission_documents)) == len(addresses)
    for found_permission_document in found_permission_documents:
        id = found_permission_document.get('id') 
        print("found id: "+ id)
        # Testing the get permission documents Lambda
        LOGGER.info('Testing the get permission document Lambda')
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.get(base_url + '/public/GET/v0/permission-documents/' + id, headers=headers)
        result = response.json()

        LOGGER.info('Result')
        LOGGER.info(result)

        assert(response.status_code) == 200 
        assert(result.get('id')) != None 

def test_fail_not_found_get_permission_document(test_env_params):
    base_url = os.environ['BaseUrl']
    id = 'FAKE_NOT_FOUND_ADDRESS'

    # Testing the get permission documents Lambda
    LOGGER.info('Testing the get permission document Lambda')

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/permission-documents/' + id, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 404 
    found_permission_document = result
    found_permission_document.get('id') == None

