import pytest
import os
import sys
import json
import logging
import boto3
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_permission_documents.get_permission_documents import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

from_address = "from_address"
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

def test_get_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']
    
    event = {
        "multiValueQueryStringParameters": {
            "address": [from_address, resource_address]
        },
        "queryStringParameters": {
            "version": "LATEST"
        }
    }
    
    response = lambda_handler(event, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)

    # found_permission_documents = result.get('found_permission_documents')
    # not_found_permission_documents = result.get('not_found_permission_documents')
    found_permission_documents = result
    assert(found_permission_documents) != []

    for permission_document in found_permission_documents:
        if permission_document.get('address') == from_address:
            from_permission_document = permission_document.get('permission_document')
        if permission_document.get('address') == resource_address: 
            resource_permission_document = permission_document.get('permission_document')

    assert(from_permission_document) == example_permission_document
    assert(resource_permission_document) == example_permission_document

def test_get_all_versions_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']
    
    event = {
        "multiValueQueryStringParameters": {
            "address": [from_address]
        },
        "queryStringParameters": {
            "version": "ALL"
        }
    }
    
    response = lambda_handler(event, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)

    # found_permission_documents = result.get('found_permission_documents')
    # not_found_permission_documents = result.get('not_found_permission_documents')
    found_permission_documents = result
    assert(len(found_permission_documents)) > len(event['multiValueQueryStringParameters']['address'])

    for permission_document in found_permission_documents:
        assert(permission_document.get('address')) == from_address


def test_get_no_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = {
        "multiValueQueryStringParameters": {
            "address": ["fake_from_address", "fake_resource_address"]
        },
        "queryStringParameters": {
            "version": "LATEST"
        }
    }
    
    response = lambda_handler(event, context = {})
    assert response["statusCode"] == 200    
    
    result = json.loads(response['body'])
    LOGGER.info('%s %s', 'body:', result)

    # found_permission_documents = result.get('found_permission_documents')
    # not_found_permission_documents = result.get('not_found_permission_documents')

    found_permission_documents = result
    assert(found_permission_documents) == []
    # assert(len(not_found_permission_documents)) == len(event.get("multiValueQueryStringParameters").get("address"))



def test_get_only_1_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = {
        "multiValueQueryStringParameters": {
            "address": [from_address, "fake_resource_address"]
        },
        "queryStringParameters": {
            "version": "LATEST"
        }
    }
    
    response = lambda_handler(event, context = {})
    assert response["statusCode"] == 200    
    
    result = json.loads(response['body'])
    LOGGER.info('%s %s', 'body:', result)

    # found_permission_documents = result.get('found_permission_documents')
    # not_found_permission_documents = result.get('not_found_permission_documents')
    found_permission_documents = result

    assert(len(found_permission_documents)) == 1
    # assert(len(not_found_permission_documents)) == 1

    for permission_document in found_permission_documents:
        if permission_document.get('address') == from_address:
            from_permission_document = permission_document.get('permission_document')

    assert(from_permission_document) == example_permission_document


def test_get_for_version_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']

    event = {
        "multiValueQueryStringParameters": {
            "address": [from_address]
        },
        "queryStringParameters": {
            "version": "v1"
        }
    }
    
    response = lambda_handler(event, context = {})
    assert response["statusCode"] == 200    
    
    result = json.loads(response['body'])
    LOGGER.info('%s %s', 'body:', result)

    # found_permission_documents = result.get('found_permission_documents')
    # not_found_permission_documents = result.get('not_found_permission_documents')
    found_permission_documents = result

    assert(len(found_permission_documents)) == 1

    for permission_document in found_permission_documents:
        if permission_document.get('address') == from_address:
            from_permission_document = permission_document.get('permission_document')

    assert(from_permission_document) == example_permission_document

example_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
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
        {"address": from_address, "version": "v1", "type": "source_permission_document", "signature": "948943987345784389348934", "is_latest": False, "permission_document": example_permission_document},
        {"address": from_address, "version": "LATEST", "type": "source_permission_document", "signature": "32892983489439034", "is_latest": True, "permission_document": example_permission_document},
        {"address": from_address, "version": "v2", "type": "source_permission_document", "signature": "32892983489439034", "is_latest": True, "permission_document": example_permission_document},
        {"address": resource_address, "version": "v1", "type": "source_permission_document", "signature": "89328938738732783", "is_latest": False, "permission_document": example_permission_document},
        {"address": resource_address, "version": "LATEST", "type": "source_permission_document", "signature": "32389287478484939043", "is_latest": True, "permission_document": example_permission_document},
        {"address": resource_address, "version": "v2", "type": "source_permission_document", "signature": "32389287478484939043", "is_latest": True, "permission_document": example_permission_document},
    ]

    for tx in txs:
        table.put_item(Item=tx)

