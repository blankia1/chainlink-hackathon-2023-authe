import pytest
import os
import sys
import json
import logging
import boto3
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_transaction.get_transaction import lambda_handler
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

def test_get_transactions_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    
    event = {
        "pathParameters": {
            "transaction_hash": transaction_hash
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

    transaction = result
    assert(transaction) != []
    
    assert(transaction.get("hash")) == transaction_hash


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

transaction = {
    "nonce": "5",
    "transaction_index": "105",
    "from_address": "0x560ecf1541389d71484374cfeb750847525582be",
    "to_address": "0xe915a8112609f0a5cbe55a23f531bef6290adb31",
    "value": "25113311404304522",
    "gas": "78979",
    "gas_price": "15452670046",
    "input": "0x",
    "receipt_cumulative_gas_used": "11198339",
    "receipt_gas_used": "49803",
    "receipt_contract_address": None,
    "receipt_root": None,
    "receipt_status": "1",
    "block_timestamp": "2023-03-17T08:52:23.000Z",
    "block_number": "16846467",
    "block_hash": "0x31016b268e395380199eb24402f159b07518cb1826fb22f273251716d92dd7d5",
    "transfer_index": [
        16846467,
        105
    ],
    "logs": [
        {
            "log_index": "280",
            "transaction_hash": "0xc3cc7e98293f79c090f90c4af0bf0f8999486dcbb3174031032e92c0b4ce4cb0",
            "transaction_index": "105",
            "address": "0xe915a8112609f0a5cbe55a23f531bef6290adb31",
            "data": "0x0000000000000000000000000000000000000000000000000059386c7563288a",
            "topic0": "0x1bb9fb49058794ee4e0f88f3c95c10019922d0b1c6f27da1ee2a98ad19d9b308",
            "topic1": "0x000000000000000000000000560ecf1541389d71484374cfeb750847525582be",
            "topic2": None,
            "topic3": None,
            "block_timestamp": "2023-03-17T08:52:23.000Z",
            "block_number": "16846467",
            "block_hash": "0x31016b268e395380199eb24402f159b07518cb1826fb22f273251716d92dd7d5",
            "transfer_index": [
                16846467,
                105,
                280
            ],
            "transaction_value": "25113311404304522"
        }
    ]
}
@pytest.fixture
def data_table_with_transactions(data_table):
    table = boto3.resource("dynamodb", os.environ['Region']).Table(data_table)

    txs = [
    {
        "address": "0x560ecf1541389d71484374cfeb750847525582be", # Custom added
        "hash": "0xc3cc7e98293f79c090f90c4af0bf0f8999486dcbb3174031032e92c0b4ce4cb0",
        "chain": "eth", # Custom added
        "transaction": transaction
    },
    ]

    for tx in txs:
        table.put_item(Item=tx)

        

