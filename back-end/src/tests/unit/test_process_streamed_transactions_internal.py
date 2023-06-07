import pytest
import os
import sys
import json
import logging
import moto
import boto3
import responses
import requests
from responses import matchers

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.process_streamed_transactions_internal.process_streamed_transactions_internal import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

example_unconfirmed_stream_transaction = {
	"Records": [{
		"body": "{\"confirmed\":false,\"chainId\":\"0xaa36a7\",\"streamId\":\"a892224b-ed66-4317-9301-dc01a272af00\",\"tag\":\"AuthEProxy\",\"retries\":0,\"block\":{\"number\":\"3561457\",\"hash\":\"0x2858ce3384f71288f6c03a3d2c31c6d874c9133aee471f18427845cded59f192\",\"timestamp\":\"1685085528\"},\"logs\":[],\"txs\":[{\"hash\":\"0x20c1b12895f5f57c6976388572cf3ca137d5cc93b08c2c7bd9dc3bf33510399f\",\"gas\":\"33086\",\"gasPrice\":\"1500000010\",\"nonce\":\"264\",\"input\":\"0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000\",\"transactionIndex\":\"56\",\"fromAddress\":\"0x78cf1d91c94667a4a6615829e394c9cce58fec9e\",\"toAddress\":\"0x0d84b1a4a01ea753cf7a58061010ec69bd484d47\",\"value\":\"0\",\"type\":\"2\",\"v\":\"1\",\"r\":\"68623677568783239942890942037904486350924283675994943669472078826599409570736\",\"s\":\"46220654584388056924474479272221784186174141546940106925291713539677290590337\",\"receiptCumulativeGasUsed\":\"10313961\",\"receiptGasUsed\":\"30926\",\"receiptContractAddress\":null,\"receiptRoot\":null,\"receiptStatus\":\"1\"}]}",
	}]
}

example_confirmed_stream_transaction = {
	"Records": [{
		"body": "{\"confirmed\":true,\"chainId\":\"0xaa36a7\",\"streamId\":\"a892224b-ed66-4317-9301-dc01a272af00\",\"tag\":\"AuthEProxy\",\"retries\":0,\"block\":{\"number\":\"3561457\",\"hash\":\"0x2858ce3384f71288f6c03a3d2c31c6d874c9133aee471f18427845cded59f192\",\"timestamp\":\"1685085528\"},\"logs\":[],\"txs\":[{\"hash\":\"0x20c1b12895f5f57c6976388572cf3ca137d5cc93b08c2c7bd9dc3bf33510399f\",\"gas\":\"33086\",\"gasPrice\":\"1500000010\",\"nonce\":\"264\",\"input\":\"0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000\",\"transactionIndex\":\"56\",\"fromAddress\":\"0x78cf1d91c94667a4a6615829e394c9cce58fec9e\",\"toAddress\":\"0x0d84b1a4a01ea753cf7a58061010ec69bd484d47\",\"value\":\"0\",\"type\":\"2\",\"v\":\"1\",\"r\":\"68623677568783239942890942037904486350924283675994943669472078826599409570736\",\"s\":\"46220654584388056924474479272221784186174141546940106925291713539677290590337\",\"receiptCumulativeGasUsed\":\"10313961\",\"receiptGasUsed\":\"30926\",\"receiptContractAddress\":null,\"receiptRoot\":null,\"receiptStatus\":\"1\"}]}",
	}]
}

example_erc20_unconfirmed_stream_transaction = {
	"Records": [{
		"body": "{\"confirmed\":true,\"chainId\":\"0xaa36a7\",\"streamId\":\"a892224b-ed66-4317-9301-dc01a272af00\",\"tag\":\"CustomERC20\",\"retries\":0,\"block\":{\"number\":\"3561457\",\"hash\":\"0x2858ce3384f71288f6c03a3d2c31c6d874c9133aee471f18427845cded59f192\",\"timestamp\":\"1685085528\"},\"logs\":[],\"txs\":[{\"hash\":\"0x20c1b12895f5f57c6976388572cf3ca137d5cc93b08c2c7bd9dc3bf33510399f\",\"gas\":\"33086\",\"gasPrice\":\"1500000010\",\"nonce\":\"264\",\"input\":\"0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000\",\"transactionIndex\":\"56\",\"fromAddress\":\"0x78cf1d91c94667a4a6615829e394c9cce58fec9e\",\"toAddress\":\"0x0d84b1a4a01ea753cf7a58061010ec69bd484d47\",\"value\":\"0\",\"type\":\"2\",\"v\":\"1\",\"r\":\"68623677568783239942890942037904486350924283675994943669472078826599409570736\",\"s\":\"46220654584388056924474479272221784186174141546940106925291713539677290590337\",\"receiptCumulativeGasUsed\":\"10313961\",\"receiptGasUsed\":\"30926\",\"receiptContractAddress\":null,\"receiptRoot\":null,\"receiptStatus\":\"1\"}], \"erc20Transfers\":[{\"transactionHash\":\"0x89a44dc8872747ed291f5a3eb1a9bea8a317ab74d65fb3ea135be7bf4165ffaf\",\"logIndex\":\"21\",\"contract\":\"0xafe39f6b68464223c49c457f94628d26173ff8b6\",\"from\":\"0x78cf1d91c94667a4a6615829e394c9cce58fec9e\",\"to\":\"0x560ecf1541389d71484374cfeb750847525582be\",\"value\":\"1000000000000000000\",\"tokenName\":\"AuthE Coin\",\"tokenSymbol\":\"AuthE\",\"tokenDecimals\":\"18\",\"valueWithDecimals\":\"1\",\"possibleSpam\":true}]}",
	}]
}


# Mock the API Responses -> https://github.com/getsentry/responses#basics
decoded_oracle_response_return_values = {
    "f": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
    "t": "0x22221C7656EC7ab88b098defB751B7401B5f6d11111",
    "n": "transfer",
    "d": "data_bytes_here",
    "r": "resource_address"
}

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

@responses.activate
def test_process_streamed_unconfirmed_transactions_internal_lambda_handler(test_env_params, data_table, data_table_events):
    base_url = os.environ['BaseUrl']
    # Mock Decode Lambda API call
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/decode',
        json=decoded_oracle_response_return_values,
        status=200,
    )	

    response = lambda_handler(example_unconfirmed_stream_transaction, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    # LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)
    LOGGER.info(result)
    
def test_process_streamed_confirmed_transactions_internal_lambda_handler(test_env_params, data_table, data_table_events):
    base_url = os.environ['BaseUrl']
    # Mock Decode Lambda API call
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/decode',
        json=decoded_oracle_response_return_values,
        status=200,
    )	
	
    response = lambda_handler(example_confirmed_stream_transaction, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    # LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)
    LOGGER.info(result)

def test_erc20_process_streamed_confirmed_transactions_internal_lambda_handler(test_env_params, data_table, data_table_events):
    base_url = os.environ['BaseUrl']
    # Mock Decode Lambda API call
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/decode',
        json=decoded_oracle_response_return_values,
        status=200,
    )	
	
    response = lambda_handler(example_erc20_unconfirmed_stream_transaction, context = {})
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

@pytest.fixture
def data_table_events():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", os.environ['Region'])
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "address", "AttributeType": "S"},
				{"AttributeName": "org", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
            ],
            TableName=os.environ['EventsDynamoDBTableName'],
            KeySchema=[
                {"AttributeName": "address", "KeyType": "HASH"},
                {"AttributeName": "created_at", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
            {
                'IndexName': 'events-org-index',
                'KeySchema': [
                    {
                        'AttributeName': 'org',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'created_at',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            }]
        )
		
        yield os.environ['EventsDynamoDBTableName']

