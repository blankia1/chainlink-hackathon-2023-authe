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
from functions.update_permission_document.update_permission_document import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')
from_address = "0x71c7656ec7ab88b098defb751b7401b5f6d8976f"
resource_address = "resource_address"
id = "o34io4f3of3nf434nlffn"

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
def test_update_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
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
        "pathParameters": {
            "id": id
        }
    }

    context = {}
    
    result = lambda_handler(event, context)
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    
    

def test_fail_update_publish_status_permission_document_lambda_handler(test_env_params, data_table, data_table_with_transactions):
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
        "body": json.dumps(example_fail_published_extended_permission_document_obj),
        "pathParameters": {
            "id": "weoinednidwnekledwlkn"
        }
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

example_published_extended_permission_document_obj = {
    'address': '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
    'signature': 'ADD_SIGNATURE_HERE',
    'status': 'published',
    'chain': 'sepolia',
    "permission_document": example_permission_document_obj
}

example_fail_published_extended_permission_document_obj = {
    'address': '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
    'signature': 'ADD_SIGNATURE_HERE',
    'status': 'draft',
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
        {"address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f", "version": "draft_o34io4f3of3nf434nlffn", "id": "o34io4f3of3nf434nlffn", "status": "draft", "type": "source_permission_document", "signature": "948943987345784389348934", "permission_document": example_permission_document_obj},
        {"address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f", "version": "draft_o34io4f3of3nf434nlffn", "id": "weoinednidwnekledwlkn", "status": "published", "type": "source_permission_document", "signature": "948943987345784389348934", "permission_document": example_permission_document_obj},
        # {"address": from_address, "version": "v1", "id": "o34io4f3of3nf434nlffn", "status": "draft", "type": "source_permission_document", "signature": "948943987345784389348934", "permission_document": example_permission_document_obj},
        # {"address": from_address, "version": "LATEST", "id": "l3kn4kn43kln4knl43kln43kln43", "type": "source_permission_document", "version_ref": 2, "signature": "32892983489439034", "permission_document": example_permission_document_obj},
        # {"address": from_address, "version": "v2", "id": "8324373984798439023hcfhfnjkjndc", "type": "source_permission_document", "signature": "32892983489439034", "permission_document": example_permission_document_obj},
        # {"address": resource_address, "version": "v1", "id": "lfk334knlfknlknf4knlfknlf34", "type": "source_permission_document","signature": "89328938738732783", "permission_document": example_permission_document_obj},
        # {"address": resource_address, "version": "LATEST", "id": "kllk34kln34knllk4nkn3fkl34", "type": "source_permission_document", "version_ref": 2, "signature": "32389287478484939043", "permission_document": example_permission_document_obj},
        # {"address": resource_address, "version": "v2", "id": "lnkfkn34kln3knf3kn43kl43kln43k4", "type": "source_permission_document", "signature": "32389287478484939043", "permission_document": example_permission_document_obj},
        # {"address": "fail_version_ref_mismatch", "version": "LATEST", "id": "k43lnnkln43knl43knlf34fknlfklnf4", "version_ref": 1, "type": "source_permission_document", "signature": "32389287478484939043", "permission_document": example_permission_document_obj},
        # {"address": "fail_version_ref_mismatch", "version": "v1", "id": "lk4n3kln34nkl43knl43nkl4fklndsklcvsasdjkn", "type": "source_permission_document", "signature": "89328938738732783", "permission_document": example_permission_document_obj},
        # {"address": "fail_version_ref_mismatch", "version": "v2", "id": "alcdsjnsdjnlqllmkqlkmqkl", "type": "source_permission_document", "signature": "32389287478484939043", "permission_document": example_permission_document_obj},
    ]

    for tx in txs:
        table.put_item(Item=tx)