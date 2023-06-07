import pytest
import os
import sys
import json
import logging
import responses
import requests

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.validate_transaction.validate_transaction import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

from_address = "0x71c7656ec7ab88b098defb751b7401b5f6d8976f"
resource_address = "resource_address"
default_resource_address_permissions = {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "*"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
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

def test_validate_transaction_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }
    
    permission_documents = {
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
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
                    "Principal": ["*", "0x1234567890123456789012345678901234567890"],
                    "Resource": ["*", "0x1234567890123456789012345678901234567890"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(permission_documents)
    }

    LOGGER.error(event)
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    

def test_validate_transaction_allow_all_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_all_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200   

def test_validate_transaction_allow_transfer_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_transfer_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200

def test_validate_transaction_allow_transfer_to_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "allow_to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_transfer_to_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200

    # But deny sending to other addresses
    oracle_decoded_request = {
        "f": from_address,
        "t": "deny_to_address_that_is_not_in_principal_list",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_transfer_to_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403

def test_validate_transaction_allow_transfer_to_on_specific_resource_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "allow_to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_transfer_to_on_specific_resource_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.error('%s %s', 'result:', result)

    assert result["statusCode"] == 200

    # But deny the other resources
    oracle_decoded_request = {
        "f": from_address,
        "t": "allow_to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "deny_to_resource_that_is_not_in_resource_list"
    }

    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_allow_transfer_to_on_specific_resource_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500


def test_validate_transaction_deny_all_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_all_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403   

def test_validate_transaction_deny_transfer_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_transfer_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403 


def test_validate_transaction_deny_approve_with_allow_rest_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "approve",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_approve_allow_rest_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403 

def test_validate_transaction_deny_not_mentioned_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "to_address",
        "n": "approve",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_not_mentioned_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403 

def test_validate_transaction_deny_transfer_to_lambda_handler(test_env_params):
    oracle_decoded_request = {
        "f": from_address,
        "t": "deny_to_address",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_transfer_to_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403 

    # Also deny if not in list because transfer method in general is denied
    oracle_decoded_request = {
        "f": from_address,
        "t": "allow_to_address_not_in_principal_with_deny_effect",
        "n": "transfer",
        "d": "data_bytes_here",
        "r": "resource_address"
    }   
    event = {
        "oracle_decoded_request": json.dumps(oracle_decoded_request),
        "permission_documents": json.dumps(dict_deny_transfer_to_permission_document)
    }
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 403 

dict_allow_all_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "*"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_allow_transfer_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:link:transfer",
                        "erc20:LINK:approve"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_allow_transfer_to_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:link:transfer",
                        "erc20:LINK:approve"
                    ],
                    "Principal": ["allow_to_address"],
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_allow_transfer_to_on_specific_resource_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:link:transfer",
                        "erc20:LINK:approve"
                    ],
                    "Principal": ["allow_to_address"],
                    "Resource": [resource_address]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_deny_all_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Deny",
                    "Action": [
                        "*"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_deny_transfer_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Deny",
                    "Action": [
                        "erc20:LINK:transfer",
                        "erc20:LINK:approve"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_deny_approve_allow_rest_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:LINK:transfer",
                        "transfer",
                        "transferFrom",
                        "mint",
                        "allowance"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                },
                {
                    "Sid": "TestPermission",
                    "Effect": "Deny",
                    "Action": [
                        "approve"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                },
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_deny_not_mentioned_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Allow",
                    "Action": [
                        "erc20:LINK:transfer",
                        "transfer",
                        "transferFrom",
                        "mint",
                        "allowance"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                },
                {
                    "Sid": "TestPermission",
                    "Effect": "Deny",
                    "Action": [
                        "random"
                    ],
                    "Principal": ["*"],
                    "Resource": ["*"]
                },
            ]
        },
        resource_address: default_resource_address_permissions
    }

dict_deny_transfer_to_permission_document = {  
        from_address: {
            "Version": "2023-05-11",
            "Signature": "o3289438973478348949023-0-030-23",
            "Statement": [
                {
                    "Sid": "TestPermission",
                    "Effect": "Deny",
                    "Action": [
                        "erc20:LINK:transfer",
                        "erc20:LINK:approve"
                    ],
                    "Principal": "deny_to_address",
                    "Resource": ["*"]
                }
            ]
        },
        resource_address: default_resource_address_permissions
    }