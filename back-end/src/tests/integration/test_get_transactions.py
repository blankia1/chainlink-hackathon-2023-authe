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

def test_get_transactions(test_env_params):
    # First get based on address
    base_url = os.environ['BaseUrl']
    addresses = ['0x78cf1d91c94667a4a6615829e394c9cce58fec9e', '0x560ecf1541389d71484374cfeb750847525582be']
    chain = 'sepolia'

    # Testing the get transactions Lambda
    LOGGER.info('Testing the get transactions Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions?', params={'address': addresses, 'chain': chain}, headers=headers)
    result = response.json()

    found_transactions = result

    assert(len(found_transactions)) != 0
    LOGGER.info("Found number of transactions: " + str(len(found_transactions)))        

def test_fail_not_found_get_transactions(test_env_params):
    base_url = os.environ['BaseUrl']
    addresses = ['FAKE_NOT_FOUND_ADDRESS']
    chain = 'eth'

    # Testing the get transactions Lambda
    LOGGER.info('Testing the get transactions Lambda')

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions?', params={'address': addresses, 'chain': chain}, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    found_transactions = result
    found_transactions == []

