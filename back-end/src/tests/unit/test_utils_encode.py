import pytest
import os
import sys
import json
import logging

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.utils_encode.utils_encode import lambda_handler
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

def test_utils_encode_lambda_handler(test_env_params):
    # messages_to_encode = [ {"address": "0x78Cf1D91C94667a4a6615829e394C9CCe58fEc9E"}, {"string": "0xbA00a6d977EB25E3edDF59F687b5cC03CA27525A"}, {"string": "transfer"}, {"string": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000"}]
    messages_to_encode = [ {"address": "0x78Cf1D91C94667a4a6615829e394C9CCe58fEc9E"}, {"address": "0x2f307e362707a7e4f9658f7719e04d29538ae63b"}, {"string": "transfer"}, {"string": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000"}]
    # messages_to_encode = [ {"address": "0x78Cf1D91C94667a4a6615829e394C9CCe58fEc9E"}, {"string": "transfer"}, {"string": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000"}]

    
    event = {
        "messages_to_encode": messages_to_encode,
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    assert(body.get('encoded_message')) == "0x6bc320072543f2c937b696b9cc47339626245833b7c4319cf549ec00963c0069"
