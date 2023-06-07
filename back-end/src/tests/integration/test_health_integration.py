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

def test_health(test_env_params):
    base_url = os.environ['BaseUrl']

    # Testing the health Lambda
    LOGGER.info('Testing the health Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test', 'Source-Region': 'us-west-2', 'Destination-Region': 'us-west-2'}
        response = requests.get(base_url + '/public/GET/health', headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from health Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    
    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200    
    assert(result.get('environment').get('env')) == 'sandbox'
    assert(result.get('environment').get('region')) == 'us-west-2'
    assert(result.get('environment').get('region_alias')) == 'pdx'
    assert(result.get('environment').get('component')) == 'lambda'
    assert(result.get('environment').get('project')) != None

    assert(headers.get('Source-Region')) == 'us-west-2'
    assert(headers.get('Destination-Region')) == 'us-west-2'
    assert(headers.get('Source-Platform')) == 'integration_test'