import pytest
import os
import sys
import json
import logging
import boto3
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_transactions_internal.get_transactions_internal import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

# from_address = "0x560ecf1541389d71484374cfeb750847525582be"
# chain = "sepolia"

# from_address = "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"
# chain = "eth"

from_address = "0x71c7656ec7ab88b098defb751b7401b5f6d8976f"
chain = "sepolia"

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def test_get_transactions_internal_lambda_handler(test_env_params, data_table):
    
    event = {
        "multiValueQueryStringParameters": {
            "address": [from_address]
        },
        "queryStringParameters": {
            "chain": chain
        }
    }
    
    response = lambda_handler(event, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    # LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)
    LOGGER.info(result)
    
@pytest.fixture
def data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", os.environ['Region'])
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "address", "AttributeType": "S"},
                {"AttributeName": "hash", "AttributeType": "S"},
				{"AttributeName": "org", "AttributeType": "S"},
                {"AttributeName": "block_number", "AttributeType": "S"},
            ],
            TableName=os.environ['TransactionsDynamoDBTableName'],
            KeySchema=[
                {"AttributeName": "hash", "KeyType": "HASH"}
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
            {
                'IndexName': 'transactions-address-block-index',
                'KeySchema': [
                    {
                        'AttributeName': 'address',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'block_number',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            },
				{
                'IndexName': 'transactions-org-block-index',
                'KeySchema': [
                    {
                        'AttributeName': 'org',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'block_number',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            }]
        )
 
        yield os.environ['TransactionsDynamoDBTableName']