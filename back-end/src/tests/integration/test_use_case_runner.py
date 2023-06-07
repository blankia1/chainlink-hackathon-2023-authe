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

# def test_use_case_runner_lambda(test_env_params):
#     base_url = os.environ['BaseUrl']
#     from_address = '0x71c7656ec7ab88b098defb751b7401b5f6d8976f'
#     to_address = '0x71c7656ec7ab88b098defb751b7401b5f6d8976f'
#     data= 'data_bytes_here'
#     function_name = "transfer"
#     resource_address = "0xca8fa8f0b631ecdb18cda619c4fc9d197c8affca"

#     # Testing the update permission documents Lambda
#     LOGGER.info('Testing the update permission documents Lambda')
#     try:
#         headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
#         response = requests.get(base_url + '/public/GET/v0?f=' + from_address + '&t=' + to_address + '&d=' + data + '&n=' + function_name + '&r=' + resource_address, headers=headers)
#         result = response.json()
#         if response.status_code != 200:
#             raise Exception("Error from use-case-runner Lambda", result)  
#     except Exception as err:
#         LOGGER.error("Unexpected error: %s" % err)

#     LOGGER.info('Result')
#     LOGGER.info(result)

#     assert(response.status_code) == 200 
#     assert(result.get('message')) == '0x68747470733a2f2f697066732e696f2f697066732f516d5358416257356b716e3259777435444c336857354d736a654b4a4839724c654c6b51733362527579547871313f66696c656e616d653d73756e2d636861696e6c696e6b2e676966' 

 
def test_fail_app_not_allowed_403_use_case_runner_lambda(test_env_params):
    base_url = os.environ['BaseUrl']
    from_address = '0x560EcF1541389d71484374CFeb750847525582be'
    to_address = '0x560EcF1541389d71484374CFeb750847525582be'
    data= '0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000'
    function_name = "NOT_ALLOWED_METHOD"
    resource_address = "0xca8fa8f0b631ecdb18cda619c4fc9d197c8affca"

    # Testing the update permission documents Lambda
    LOGGER.info('Testing the update permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.get(base_url + '/public/GET/v0?f=' + from_address + '&t=' + to_address + '&d=' + data + '&n=' + function_name + '&r=' + resource_address, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from use-case-runner Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 403 
    assert(result.get('message')) == 'forbidden' 
    assert(result.get('reason')) == 'App 403 Forbidden' 


    