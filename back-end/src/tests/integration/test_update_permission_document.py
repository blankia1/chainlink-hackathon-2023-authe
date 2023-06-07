import pytest
import os
import sys
import json
import logging
import boto3
import moto
import requests
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

@pytest.fixture()
def test_env_params():
    """Load environment variables"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

good_payload = {
        "Version": "2023-05-11",
        "Signature": "0x4ee1be11f0c140c32034c47c6267b396ba20177627d9c6d7e7634445d24b83084fe6637e87aec7095cb01f2d250e58cc7d026c9e00bae6811b9e5ffe221a130f1b",
        "Statement": [
            {
                "Sid": "TestPermission",
                "Effect": "Allow",
                "Action": [
                    "erc20:LINK:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            }
        ]
    }
replace_good_payload = {
    "Version": "2023-05-11",
    "Signature": "0xd4464521bcf921babee2da7388df5136e75cd55f0b33947987b80a59e1a314da641da7e318a377b6e8807571496e7e10dd01235d1d1ac66f334420c37afbf9381c",
    "Statement": [
        {
            "Sid": "TestPermission2",
            "Effect": "Deny",
            "Action": [
                "erc20:LINK:approve"
            ],
            "Principal": ["*"],
            "Resource": ["*"]
        }
    ]
}

bad_payload = {
        "Version": "2023-05-11",
        "Signature": "FAKE_SIGNATURE", # Fake signature
        "Statement": [
            {
                "Sid": "TestPermission",
                "Effect": "Allow",
                "Action": [
                    "erc20:LINK:transfer"
                ],
                "Principal": ["*"],
                "Resource": ["*"]
            }
        ]
    }


example_published_extended_permission_document_obj =   {
 	"address": "0x560EcF1541389d71484374CFeb750847525582be",
 	"status": "published",
 	"chain": "sepolia",
 	"signature": "0x4ee1be11f0c140c32034c47c6267b396ba20177627d9c6d7e7634445d24b83084fe6637e87aec7095cb01f2d250e58cc7d026c9e00bae6811b9e5ffe221a130f1b",
 	"version": "version",
 	"permission_document": good_payload
 }

example2_draft_extended_permission_document_obj =   {
 	"address": "0x560EcF1541389d71484374CFeb750847525582be",
 	"status": "draft",
 	"chain": "sepolia",
 	"signature": "0xd4464521bcf921babee2da7388df5136e75cd55f0b33947987b80a59e1a314da641da7e318a377b6e8807571496e7e10dd01235d1d1ac66f334420c37afbf9381c",
 	"version": "version",
 	"permission_document": replace_good_payload
 }

example3_draft_extended_permission_document_obj =   {
 	"address": "0x560EcF1541389d71484374CFeb750847525582be",
 	"status": "draft",
 	"chain": "sepolia",
 	"signature": "FAKE_SIGNATURE",
 	"version": "version",
 	"permission_document": bad_payload
 }

example4_draft_extended_permission_document_obj =   {
 	"address": "0x560EcF1541389d71484374CFeb750847525582be",
 	"status": "draft",
 	"chain": "sepolia",
 	"signature": "0x4ee1be11f0c140c32034c47c6267b396ba20177627d9c6d7e7634445d24b83084fe6637e87aec7095cb01f2d250e58cc7d026c9e00bae6811b9e5ffe221a130f1b",
 	"version": "version",
 	"permission_document": good_payload
 }

def test_update_permission_documents(test_env_params):
    base_url = os.environ['BaseUrl']
    address = '0x560EcF1541389d71484374CFeb750847525582be'

    # First create one in status draft
    # Testing the create permission document Lambda
    LOGGER.info('Testing the create permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents', json=example2_draft_extended_permission_document_obj, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from create permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('id')) != None

    id = result.get('id')
    LOGGER.info("Id: " + id)

    # Testing the update permission documents Lambda
    LOGGER.info('Testing the update permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.put(base_url + '/public/ANY/v0/permission-documents/' + id, json=example4_draft_extended_permission_document_obj , headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from update permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('message')) == 'success' 

    # Change the permission document to the replace_good_payload
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.put(base_url + '/public/ANY/v0/permission-documents/' + id, json=example2_draft_extended_permission_document_obj, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from update permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('message')) == 'success'    

    # Get the permission document
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.get(base_url + '/public/GET/v0/permission-documents/' + id, headers=headers)
        result = response.json() 
        if response.status_code != 200:
            raise Exception("Error from update permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 

    # # found_permission_documents = result.get('found_permission_documents')
    # # not_found_permission_documents = result.get('not_found_permission_documents')
    found_permission_document = result
    assert(found_permission_document.get('id')) == id

    from_permission_document = found_permission_document.get('permission_document')

    assert(from_permission_document) == replace_good_payload

    # Publish it
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.put(base_url + '/public/ANY/v0/permission-documents/' + id, json=example_published_extended_permission_document_obj, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from update permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('message')) == 'success' 

# Should not be allowed to update publish document
def test_fail_update_publish_permission_documents(test_env_params):
    base_url = os.environ['BaseUrl']
    address = '0x560EcF1541389d71484374CFeb750847525582be'

    # First create one in status draft
    # Testing the create permission document Lambda
    LOGGER.info('Testing the create permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/public/ANY/v0/permission-documents', json=example_published_extended_permission_document_obj, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from create permission documents Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('id')) != None

    id = result.get('id')
    LOGGER.info("Id: " + id)

    # Testing the update permission documents Lambda
    LOGGER.info('Testing the update permission documents Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.put(base_url + '/public/ANY/v0/permission-documents/' + id, json=example4_draft_extended_permission_document_obj, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from update permission documents Lambda: ", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 500 
    assert(result.get('reason')) == 'Unexpected error' 

# def test_fail_update_permission_documents(test_env_params):
#     base_url = os.environ['BaseUrl']
#     address = '0x560EcF1541389d71484374CFeb750847525582be'

#     # First create one in status draft
#     # Testing the create permission document Lambda
#     LOGGER.info('Testing the create permission documents Lambda')
#     try:
#         headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
#         response = requests.post(base_url + '/public/ANY/v0/permission-documents', json=example2_draft_extended_permission_document_obj, headers=headers)
#         result = response.json()
#         if response.status_code != 200:
#             raise Exception("Error from create permission documents Lambda", result)  
#     except Exception as err:
#         LOGGER.error("Unexpected error: %s" % err)

#     LOGGER.info('Result')
#     LOGGER.info(result)

#     assert(response.status_code) == 200 
#     assert(result.get('id')) != None

#     id = result.get('id')
#     LOGGER.info("Id: " + id)

#     # Testing the update permission documents Lambda
#     LOGGER.info('Testing the update permission documents Lambda')
#     try:
#         headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
#         response = requests.put(base_url + '/public/ANY/v0/permission-documents/' + id, json=example3_draft_extended_permission_document_obj, headers=headers)
#         result = response.json()
#         if response.status_code != 200:
#             raise Exception("Error from update permission documents Lambda: ", result)  
#     except Exception as err:
#         LOGGER.error("Unexpected error: %s" % err)

#     LOGGER.info('Result')
#     LOGGER.info(result)

#     assert(response.status_code) == 500 
#     assert(result.get('reason')) == 'Error validating the signature' 

