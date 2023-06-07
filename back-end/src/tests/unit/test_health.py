import pytest
import os
import sys
import json
import logging

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.health.health import lambda_handler
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

def test_health_lambda_handler(test_env_params):
    event = {
        "key1": "value1",
        "headers": {
            "Source-Region": "us-west-2",
            "Destination-Region": "us-west-2",
            "Source-Platform": "oracle"
        }
    }
    
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

    body = json.loads(result['body'])
    LOGGER.info('%s %s', 'body:', body)

    headers = result['headers']

    LOGGER.info('%s %s', 'headers:', headers)

    assert(body.get('environment').get('env')) == 'sandbox'
    assert(body.get('environment').get('region')) == 'us-west-2'
    assert(body.get('environment').get('region_alias')) == 'pdx'
    assert(body.get('environment').get('component')) == 'lambda'
    assert(body.get('environment').get('project')) != None

    assert(headers.get('Source-Region')) == 'us-west-2'
    assert(headers.get('Destination-Region')) == 'us-west-2'
    assert(headers.get('Source-Platform')) == 'oracle'