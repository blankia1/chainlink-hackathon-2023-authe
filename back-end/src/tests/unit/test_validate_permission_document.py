import pytest
import os
import sys
import json
import logging
import responses
import requests

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/functions')
from functions.validate_permission_document.validate_permission_document import lambda_handler
ENVIRONMENT_PARAMETERS_PATH = '../test.env.json'
LOGGER=logging.getLogger()
LOGGER.setLevel('WARNING')

@pytest.fixture()
def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def test_validate_permission_document_lambda_handler(test_env_params):   
    dict_permission_document = {
        "Version": "2023-05-11",
        "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
        "Statement": [
            {
                "Sid": "TestPermission",
                "Effect": "Allow",
                "Action": [
                    "erc20:LINK:transfer"
                ],
                "Principal": "*",
                "Resource": "*"
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
    }

    event = {
        "body": json.dumps(dict_permission_document),
    }

    # LOGGER.error('%s %s', 'event:', event)
    result = lambda_handler(event, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 200    




def test_incorrect_version_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_version_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_version_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_version_value_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

def test_incorrect_signature_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_signature_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_signature_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   


def test_incorrect_statement_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_statement_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_statement_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

def test_incorrect_sid_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_sid_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   
    
    result = lambda_handler({"body": json.dumps(dict_incorrect_sid_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   


def test_incorrect_effect_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_effect_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   
    
    result = lambda_handler({"body": json.dumps(dict_incorrect_effect_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_effect_value_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

def test_incorrect_action_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_action_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_action_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_action_value_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

def test_incorrect_principal_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_principal_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_principal_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_principal_value_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

def test_incorrect_resource_validate_permission_document_lambda_handler(test_env_params):   
    result = lambda_handler({"body": json.dumps(dict_incorrect_no_resource_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_resource_key_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

    result = lambda_handler({"body": json.dumps(dict_incorrect_resource_value_permission_document)}, context = {})
    LOGGER.info('%s %s', 'result:', result)

    assert result["statusCode"] == 500   

dict_incorrect_no_version_permission_document = {
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
        },
        {
            "Sid": "TestPermission2",
            "Effect": "Allow",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Principal": ["*",  "0x1234567890123456789012345678901234567890"],
            "Resource": ["*", "0x1234567890123456789012345678901234567890"]
        }
    ]
}

dict_incorrect_version_key_permission_document = {
    "Version2": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
        },
        {
            "Sid": "TestPermission2",
            "Effect": "Allow",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Principal": ["*",  "0x1234567890123456789012345678901234567890"],
            "Resource": ["*", "0x1234567890123456789012345678901234567890"]
        }
    ]
}

dict_incorrect_version_value_permission_document = {
    "Version": "202-02202020-2",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_no_signature_permission_document = {
    "Version": "2023-05-11",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
        },
        {
            "Sid": "TestPermission2",
            "Effect": "Allow",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Principal": ["*",  "0x1234567890123456789012345678901234567890"],
            "Resource": ["*", "0x1234567890123456789012345678901234567890"]
        }
    ]
}

dict_incorrect_signature_key_permission_document = {
    "Version": "2023-05-11",
    "Signature2": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
        },
        {
            "Sid": "TestPermission2",
            "Effect": "Allow",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Principal": ["*",  "0x1234567890123456789012345678901234567890"],
            "Resource": ["*", "0x1234567890123456789012345678901234567890"]
        }
    ]
}

dict_incorrect_no_statement_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340"
}

dict_incorrect_statement_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement2": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_sid_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid2": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_no_sid_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_no_effect_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_effect_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect2": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_effect_value_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow2",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_no_action_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow2",
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_action_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action2": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_action_value_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer2"
            ],
            "Principal": "*",
            "Resource": "*"
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
}

dict_incorrect_no_principal_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow2",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Resource": "*"
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
}

dict_incorrect_principal_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal2": "*",
            "Resource": "*"
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
}

dict_incorrect_principal_value_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*2",
            "Resource": "*"
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
}

dict_incorrect_no_resource_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow2",
            "Action": [
                "erc20:ETH:transfer"
            ],
            "Principal": "*"
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
}

dict_incorrect_resource_key_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource2": "*"
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
}

dict_incorrect_resource_value_permission_document = {
    "Version": "2023-05-11",
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340",
    "Statement": [
        {
            "Sid": "TestPermission",
            "Effect": "Allow",
            "Action": [
                "erc20:LINK:transfer"
            ],
            "Principal": "*",
            "Resource": "*2"
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
}