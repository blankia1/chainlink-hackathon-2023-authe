import pytest
import os
import sys
import json
import logging

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_transaction_internal.get_transaction_internal import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

transaction_hash = "0xc3cc7e98293f79c090f90c4af0bf0f8999486dcbb3174031032e92c0b4ce4cb0"
chain = "eth"

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def test_get_transactions_internal_lambda_handler(test_env_params):
    
    event = {
        "pathParameters": {
            "transaction_hash": [transaction_hash]
        },
        "queryStringParameters": {
            "chain": chain
        }
    }
    
    response = lambda_handler(event, context = {})
    # LOGGER.info('%s %s', 'response:', response)

    assert response["statusCode"] == 200    
    # LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)

    transaction = result
    assert(transaction) != []
    
    assert(transaction.get("hash")) == transaction_hash
