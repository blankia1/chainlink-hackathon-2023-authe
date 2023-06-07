import pytest
import os
import sys
import json
import logging
import boto3
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.get_permission_document.get_permission_document import lambda_handler
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

def test_get_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']
    id = 'wrfijohf2hoofhi3fiurrfnnkjfwer_LATEST'
    event = {
        "pathParameters": {
            "id": id
        }
    }
    
    response = lambda_handler(event, context = {})
    # LOGGER.info('%s %s', 'result:', result)

    assert response["statusCode"] == 200    
    LOGGER.info('%s %s', 'response:', response)

    result = json.loads(response['body'])
    # LOGGER.info('%s %s', 'body:', result)

    found_permission_document = result
    assert(found_permission_document.get('id')) == id
    assert(found_permission_document.get('permission_document')) == example_permission_document


def test_get_no_permission_documents_lambda_handler(test_env_params, data_table, data_table_with_transactions):
    table_name = os.environ['PermissionDocumentsDynamoDBTableName']
    id = 'FAKE_ID'

    event = {
        "pathParameters": {
            "id": id
        }
    }
    
    response = lambda_handler(event, context = {})
    assert response["statusCode"] == 404    
    
    result = json.loads(response['body'])
    LOGGER.info('%s %s', 'body:', result)

    found_permission_document = result
    assert(found_permission_document.get('id')) == None


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
                {"AttributeName": "version", "AttributeType": "S"},
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            TableName=os.environ['PermissionDocumentsDynamoDBTableName'],
            KeySchema=[
                {"AttributeName": "address", "KeyType": "HASH"},
                {"AttributeName": "version", "KeyType": "RANGE"}
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
            {
                'IndexName': 'permission-documents-id-index',
                'KeySchema': [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL',
                }
            }]
        )

        
        
        yield os.environ['PermissionDocumentsDynamoDBTableName']

@pytest.fixture
def data_table_with_transactions(data_table):
    table = boto3.resource("dynamodb", os.environ['Region']).Table(data_table)

    txs = [
        {"address": from_address, "version": "v1", "id": "8324373984798439023hcfhfnjkjndc", "type": "source_permission_document", "signature": "948943987345784389348934", "is_latest": False, "permission_document": example_permission_document},
        {"address": from_address, "version": "LATEST", "id": "wrfijohf2hoofhi3fiurrfnnkjfwer_LATEST", "type": "source_permission_document", "signature": "32892983489439034", "is_latest": True, "permission_document": example_permission_document},
        {"address": from_address, "version": "v2", "id": "bf26a0060f0241308c07fdfef5577103_LATEST", "type": "source_permission_document", "signature": "32892983489439034", "is_latest": True, "permission_document": example_permission_document},
        {"address": resource_address, "version": "v1", "id": "89328ufhuivrecnnojic2eijo22", "type": "source_permission_document", "signature": "89328938738732783", "is_latest": False, "permission_document": example_permission_document},
        {"address": resource_address, "version": "LATEST", "id": "wlnekknjwdlknjcjklncnwjkelwnklej_LATEST", "type": "source_permission_document", "signature": "32389287478484939043", "is_latest": True, "permission_document": example_permission_document},
        {"address": resource_address, "version": "v2", "id": "jo298h4f89238h24e2osdjnkwejnw", "type": "source_permission_document", "signature": "32389287478484939043", "is_latest": True, "permission_document": example_permission_document},
    ]

    for tx in txs:
        table.put_item(Item=tx)

