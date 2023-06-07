import pytest
import os
import sys
import json
import logging
import boto3
import requests

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
    "f": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
    "t": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47",
    "n": "transfer",
    "d": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000",
    "r": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47"
}

def test_utils_validate_signature(test_env_params):
    base_url = os.environ['BaseUrl']
    address = "0x71c7656ec7ab88b098defb751b7401b5f6d8976f"

    # Testing the Lambda
    LOGGER.info('Testing the utils decode Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/utils/decode', json=good_payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from utils decode Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    
    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200    
    # assert(result.get('d')) == "[['string', '_value', 'https://0iocgc3pk6.execute-api.us-west-2.amazonaws.com/']]"  
