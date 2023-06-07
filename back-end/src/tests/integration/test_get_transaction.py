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
    "signature": "0x63448e264ad492506667412c54ba2f0473909b6bfa2b7558342700f2150dd949254448141616618017d17ab8432a34932ee0184024de1446b775e8a403a7d4601b",
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
        "Signature": "0x63448e264ad492506667412c54ba2f0473909b6bfa2b7558342700f2150dd949254448141616618017d17ab8432a34932ee0184024de1446b775e8a403a7d4601b"
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

def test_get_transactions(test_env_params):
    base_url = os.environ['BaseUrl']
    chain = 'sepolia'
    addresses = ["0x78cf1d91c94667a4a6615829e394c9cce58fec9e", "0x560ecf1541389d71484374cfeb750847525582be"]
    # First get based on address
    LOGGER.info('Testing the get transactions Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions?', params={'address': addresses, 'chain': chain}, headers=headers)
    result = response.json()

    hash = result[0].get('hash')
    # Testing the get transaction Lambda
    LOGGER.info('Testing the get transactions Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions/' + hash, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
        

def test_fail_not_found_get_transactions(test_env_params):
    base_url = os.environ['BaseUrl']
    hash = 'FAKE_NOT_FOUND_ADDRESS'

    # Testing the get transactions Lambda
    LOGGER.info('Testing the get transaction Lambda')

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions/'  + hash, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 404 
    found_transactions = result
    found_transactions == []

