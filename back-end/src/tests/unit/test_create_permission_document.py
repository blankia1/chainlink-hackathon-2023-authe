import pytest
import os
import sys
import json
import logging
import boto3
import moto
import responses
import requests
from responses import matchers

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.create_permission_document.create_permission_document import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')
from_address = "0x71c7656ec7ab88b098defb751b7401b5f6d8976f"
resource_address = "resource_address"

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
def test_create_draft_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    base_url = os.environ['BaseUrl']

    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/validate-signature',
        status=200,
        json={"message": "success"}
    ) 

    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = { 
        "body": json.dumps(example_draft_extended_permission_document_obj),
    }

    context = {}
    
    result = lambda_handler(event, context)
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

def test_create_published_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    base_url = os.environ['BaseUrl']

    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/validate-signature',
        status=200,
        json={"message": "success"}
    ) 

    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = { 
        "body": json.dumps(example_published_extended_permission_document_obj),
    }

    context = {}
    
    result = lambda_handler(event, context)
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200

def test_create_fail_duplicate_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    base_url = os.environ['BaseUrl']

    # Mock the API Responses -> https://github.com/getsentry/responses#basics
    responses.add(
        responses.POST,
        base_url + '/public/ANY/v0/utils/validate-signature',
        status=200,
        json={"message": "success"}
    ) 

    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = { 
        "body": json.dumps(example_fail_duplicate_extended_permission_document_obj),
    }

    context = {}
    
    result = lambda_handler(event, context)
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500


example_permission_document_obj = {
    "permission_document":  {
        "Version": "2023-05-11",
        "Signature": from_address,
        "Statement": [
            {
                "Sid": "TestPermission",
                "Effect": "Allow",
                "Action": [
                    "erc20:LINK:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            },
            {
                "Sid": "TestPermission2",
                "Effect": "Allow",
                "Action": [
                    "erc20:ETH:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            }
        ]
    }
}

example_draft_extended_permission_document_obj = {
    'address': '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
    'status': 'draft',
    'chain': 'sepolia',
    "permission_document": example_permission_document_obj
}

example_published_extended_permission_document_obj = {
    'address': '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
    'status': 'published',
    'signature': "INSERT_SIGNED_SIGNATURE_HERE",
    'chain': 'sepolia',
    "permission_document": example_permission_document_obj
}

example_fail_duplicate_extended_permission_document_obj = {
    'address': from_address,
    'status': 'published',
    'signature': "INSERT_SIGNED_SIGNATURE_HERE",
    'chain': 'sepolia',
    "permission_document": example_permission_document_obj
}

@pytest.fixture
def data_table():
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", os.environ['Region'])
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "address", "AttributeType": "S"},
                {"AttributeName": "version", "AttributeType": "S"}
            ],
            TableName=os.environ['PermissionDocumentsDynamoDBTableName'],
            KeySchema=[
                {"AttributeName": "address", "KeyType": "HASH"},
                {"AttributeName": "version", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        
        yield os.environ['PermissionDocumentsDynamoDBTableName']

@pytest.fixture
def data_table_with_transactions(data_table):
    table = boto3.resource("dynamodb", os.environ['Region']).Table(data_table)

    txs = [
        {"address": from_address, "version": "v1", "type": "source_permission_document", "signature": "948943987345784389348934", "permission_document": example_permission_document_obj},
        {"address": from_address, "version": "LATEST", "type": "source_permission_document", "version_ref": 1, "signature": "32892983489439034", "permission_document": example_permission_document_obj},
    ]

    for tx in txs:
        table.put_item(Item=tx)
