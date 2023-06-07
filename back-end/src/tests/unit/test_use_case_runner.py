import pytest
import os
import sys
import json
import logging
import responses
import requests
from responses import matchers

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.use_case_runner.use_case_runner import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

#  https://0iocgc3pk6.execute-api.us-west-2.amazonaws.com/sandbox?f=from&t=to&n=functionname&d=data
event = {
    "queryStringParameters": {
        "f": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
        "t": "0x22221c7656ec7ab88b098defb751b7401b5f6d11111",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }
}

# Mock the API Responses -> https://github.com/getsentry/responses#basics
decoded_oracle_response_return_values = {
    "f": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
    "t": "0x22221c7656ec7ab88b098defb751b7401b5f6d11111",
    "n": "transfer",
    "d": "data_bytes_here",
    "r": "resource_address"
}

@responses.activate
def test_use_case_runner_lambda_handler(test_env_params):
    base_url = os.environ['BaseUrl']
    # Mock Decode Lambda API call
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/decode',
        json=decoded_oracle_response_return_values,
        status=200,
    )

    # Mock Validate Lambda API call
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/transactions/validate/',
        json=decoded_oracle_response_return_values,
        status=200,
    )
    
    _from = decoded_oracle_response_return_values.get('f')
    _resource_address = decoded_oracle_response_return_values.get('r')
    addresses=[_from, _resource_address]
    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.GET,
        base_url + '/public/GET/v0/permission-documents',
        match=[matchers.query_param_matcher({'address': addresses, 'version': 'LATEST'})],
        status=200,
        json=json_data
    )

    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/permission-documents/validate/',
        status=200,
        json={"message": "success"}
    ) 

    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/encode',
        status=200,
        json={"encoded_message": "0x933e2055e9469c6bf9a6be1ff664d3934db755d82a534c0c7b1775195a9753ab"}
    ) 

    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    mocked_decode_lambda_result = json.loads(responses.calls[0].request.body)
    assert(body.get('message')) == '0x3078393333653230353565393436396336626639613662653166663636346433393334646237353564383261353334633063376231373735313935613937353361625f393433343930333934383033343338393433393834333833343930303932302d3332302d332d323032343930343230393432393034393033333439303433302d2d3334305f'
    assert(body.get('f')) == event['queryStringParameters']['f']
    assert(body.get('t')) == event['queryStringParameters']['t']
    assert(body.get('n')) == event['queryStringParameters']['n']
    assert(body.get('d')) == event['queryStringParameters']['d']

address1 = decoded_oracle_response_return_values.get('f')
address2 = decoded_oracle_response_return_values.get('r')
# Mock dummy data for now

json_data = [
    { 
        "address": address1,
        "signature": "434343565656",
        "permission_document": {
            "Version": "2023-05-11",
            "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:LINK:transfer"
                    ],
                    "Principal": "*",
                    "Resource": "*"
                },
                {
                    "Sid": "TestPermission2",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:ETH:transfer"
                    ],
                    "Principal": ["*", "0x1234567890123456789012345678901234567890"],
                    "Resource": ["*", "0x1234567890123456789012345678901234567890"]
                }
            ]
        }
    },
    {   
        "address": address2,
        "signature": "434343565656",
        "permission_document": {
            "Version": "2023-05-11",
            "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
            "Statement": [
                {
                    "Sid": "DefaultResourcePermissions",
                    "Effect": "Allow",
                    "Action": [
                        "*"
                    ],
                    "Principal": "*",
                    "Resource": "*"
                }
            ]
        }
    }]

