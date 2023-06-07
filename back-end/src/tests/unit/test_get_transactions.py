import pytest
import os
import sys
import json
import logging
import boto3
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_transactions.get_transactions import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

from_address = "0x560ecf1541389d71484374cfeb750847525582be"
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

    transactions = result
    assert(transactions) != 3
    


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

transaction1 = {
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

transaction2 =     {
    "hash": "0x3441e911d848a31488f54edf5f2fe898371bff254efdb1654059716ad0f90ae4",
    "nonce": "3",
    "transaction_index": "55",
    "from_address": "0x560ecf1541389d71484374cfeb750847525582be",
    "to_address": "0x6f8dfebaae2262f0db9c761df3db7a4c9f6d5485",
    "value": "500000000000000000",
    "gas": "21000",
    "gas_price": "15148419798",
    "input": "0x",
    "receipt_cumulative_gas_used": "4530680",
    "receipt_gas_used": "21000",
    "receipt_contract_address": None,
    "receipt_root": None,
    "receipt_status": "1",
    "block_timestamp": "2023-01-06T12:24:59.000Z",
    "block_number": "16347727",
    "block_hash": "0xd5170706d45684e6df3c559e5f76352b4bac50630e0d8abb39cdeb915ef65b08",
    "transfer_index": [
        16347727,
        55
    ]
}

transaction3 = {
    "hash": "0x65f838d03b7835a1eadddbcd3c06193629a94c19c15154df9637c2327bcb30ce",
    "nonce": "2",
    "transaction_index": "13",
    "from_address": "0x560ecf1541389d71484374cfeb750847525582be",
    "to_address": "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45",
    "value": "0",
    "gas": "324901",
    "gas_price": "14452827990",
    "input": "0x5ae401dc0000000000000000000000000000000000000000000000000000000063b819b700000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000124b858183f0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000002a5a058fc295ed000000000000000000000000000000000000000000000000000008af1a320b1b13b6300000000000000000000000000000000000000000000000000000000000000424fabb145d64652a948d72533023f6e7a623c7c53000064a0b86991c6218b36c1d19d4a2e9eb0ce3606eb480001f4c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c0000000000000000000000000000000000000000000000008af1a320b1b13b63000000000000000000000000560ecf1541389d71484374cfeb750847525582be00000000000000000000000000000000000000000000000000000000",
    "receipt_cumulative_gas_used": "25652900",
    "receipt_gas_used": "224723",
    "receipt_contract_address": None,
    "receipt_root": None,
    "receipt_status": "1",
    "block_timestamp": "2023-01-06T12:23:47.000Z",
    "block_number": "16347721",
    "block_hash": "0xb47341dde03aad63df7b372b561d48d6755c17ec0f8a0399d333c2f13294d404",
    "transfer_index": [
        16347721,
        13
    ]
}

transaction4 =  {
        "hash": "0x01163ca8083f8cdef2e4ff8a45ad88901731925a924041a33e3a30856606944b",
        "nonce": "4",
        "transaction_index": "85",
        "from_address": "0x560ecf1541389d71484374cfeb750847525582be",
        "to_address": "0x6f8dfebaae2262f0db9c761df3db7a4c9f6d5485",
        "value": "9600000000000000000",
        "gas": "21000",
        "gas_price": "14219058375",
        "input": "0x",
        "receipt_cumulative_gas_used": "9191562",
        "receipt_gas_used": "21000",
        "receipt_contract_address": None,
        "receipt_root": None,
        "receipt_status": "1",
        "block_timestamp": "2023-01-06T12:26:47.000Z",
        "block_number": "16347736",
        "block_hash": "0x0c6ef41af0b5db13cf47704d0ac35f24cf263bebd43530cd1613332c16e5206b",
        "transfer_index": [
            16347736,
            85
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
        "transaction": transaction1
    },
    {
        "address": "0x560ecf1541389d71484374cfeb750847525582be", # Custom added
        "hash": "0x3441e911d848a31488f54edf5f2fe898371bff254efdb1654059716ad0f90ae4",
        "chain": "eth", # Custom added
        "transaction": transaction2
    },
    {
        "address": "0x560ecf1541389d71484374cfeb750847525582be", # Custom added
        "hash": "0x65f838d03b7835a1eadddbcd3c06193629a94c19c15154df9637c2327bcb30ce",
        "chain": "eth", # Custom added
        "transaction": transaction3
    },
    {
        "address": "0x560ecf1541389d71484374cfeb750847525582be", # Custom added
        "hash": "0x01163ca8083f8cdef2e4ff8a45ad88901731925a924041a33e3a30856606944b",
        "chain": "sepolia", # Custom added
        "transaction": transaction4
    },
    ]
    
    for tx in txs:
        table.put_item(Item=tx)

        

