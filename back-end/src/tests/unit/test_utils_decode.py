import pytest
import os
import sys
import json
import logging

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.utils_decode.utils_decode import lambda_handler
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

def test_utils_decode_lambda_handler(test_env_params):
    event = {
        "f": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
        "t": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47",
        "n": "transfer",
        "d": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000",
        "r": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47"
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

def test_custom_utils_decode_lambda_handler(test_env_params):
    event = {
        "f": "0x560ecf1541389d71484374cfeb750847525582be",
        "t": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47",
        "n": "transfer",
        "d": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000001068637573746f6d73747566666865726500000000000000000000000000000000",
        "r": "0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47"
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)


def test_erc20_utils_decode_lambda_handler(test_env_params):
    event = {
        "f": "0x78cf1d91c94667a4a6615829e394c9cce58fec9e",
        "t": "0x560ecf1541389d71484374cfeb750847525582be",
        "n": "transfer",
        "d": "0xa9059cbb000000000000000000000000560ecf1541389d71484374cfeb750847525582be00000000000000000000000000000000000000000000000000038d7ea4c68000",
        "r": "0x779877A7B0D9E8603169DdbD7836e478b4624789"
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)