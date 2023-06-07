import os
import json
import logging
import boto3
import hashlib
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

ENVIRONMENT_PARAMETERS_PATH = '../src/tests/test.env.json'

class PermissionDocumentNotChangedException(Exception):            
    pass


def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data

def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v) 
        for k, v in dynamo_obj.items()
    }  

new_permission_document_objs = {
    "allow_all": {
        "permission_document":  {
            "Version": "2023-05-11",
            "Signature": "address",
            "Statement": [
                {
                    "Sid": "AllowAll",
                    "Effect": "Allow",
                    "Action": ["*"],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        }
    },
    "allow_transfer": {
        "permission_document":  {
            "Version": "2023-05-11",
            "Signature": "address",
            "Statement": [
                {
                    "Sid": "AllowAll",
                    "Effect": "Allow",
                    "Action": ["erc20:LINK:transfer"],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        }
    },
    "deny_all": {
        "permission_document":  {
            "Version": "2023-05-11",
            "Signature": "address",
            "Statement": [
                {
                    "Sid": "DenyAll",
                    "Effect": "Deny",
                    "Action": ["*"],
                    "Principal": ["*"],
                    "Resource": ["*"]
                }
            ]
        }
    }
}

def main():
    address_configs = [
        {"0x71c7656ec7ab88b098defb751b7401b5f6d8976f": "allow_transfer"},  
        {"0xca8fa8f0b631ecdb18cda619c4fc9d197c8affca": "allow_all"}
    ]
     
    for address_config in address_configs:
        update(address_config)

def update(address_config):
    test_env_params()
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['PermissionDocumentsDynamoDBTableName']
    client = boto3.client('dynamodb', region)
    import uuid
    id = uuid.uuid4().hex

    address = None
    permission_document_name = None
    for k, v in address_config.items():
        address = k
        permission_document_name = v

    # Load the config corresponding the address
    new_permission_document_obj = new_permission_document_objs.get(permission_document_name)
    new_permission_document = new_permission_document_obj.get('permission_document') 

    new_permission_document['Signature'] = address
    hash_object = hashlib.sha224(str(new_permission_document).encode('utf-8'))
    new_signature_hash = hash_object.hexdigest()
    new_permission_document['Signature'] = new_signature_hash

    # Find the latest existing version of the permission document
    response = client.get_item(
        TableName = DYNAMO_DB_TABLE_NAME,
        Key = {
            'address': { 'S': address },
            'version': { 'S': 'LATEST' }
        },
        ConsistentRead = True
    )

    try:
        if not response.get('Item'):
            LOGGER.info("no items yet in Dynamodb for this address")
            LOGGER.info("Creating a new permission document")
            LOGGER.info("Address: " + address)
            LOGGER.info("Id: " + id)
            LOGGER.info("Signature: " + new_signature_hash)
            LOGGER.info(str(new_permission_document))


            response = client.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Item': {
                                'address': { 'S': address },
                                'version': { 'S': 'v1' },
                                'id': { 'S': id },
                                'signature': { 'S': new_signature_hash },
                                'permission_document': python_obj_to_dynamo_obj(new_permission_document_obj).get('permission_document') 
                            },
                            'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)'
                        }
                    },
                    # Insert the LATEST version of the permission document with the new permission document info and version_ref
                    {
                        'Put': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Item': {
                                'address': { 'S': address },
                                'version': { 'S': 'LATEST' },
                                'version_ref': {'N': '1'},
                                'id': { 'S': id + "_LATEST"},
                                'signature': { 'S': new_signature_hash },
                                'permission_document': python_obj_to_dynamo_obj(new_permission_document_obj).get('permission_document')
                            }
                        }
                    }
                ]
            )
        else:
            parsed_item = dynamo_obj_to_python_obj(response['Item']) 
            old_version_ref = str(parsed_item['version_ref'])
            new_version = str(int(old_version_ref)+1)
            old_permission_document = parsed_item['permission_document']
            old_signature_hash = parsed_item['signature']

            # Need to compare signature data to not keeping on increasing versions
            if old_permission_document == str(new_permission_document) or old_signature_hash == new_signature_hash:
                LOGGER.info("Permission document has not changed")
                raise PermissionDocumentNotChangedException("Permission document has not changed", "New permission document: ",  
                    str(new_permission_document), "Old permission document: ", str(old_permission_document), 
                        "New signature:", new_signature_hash, "Old signature:", old_signature_hash )

            LOGGER.info("Creating a new permission document")
            LOGGER.info("Address: " + address)
            LOGGER.info("New Signature: " + new_signature_hash)
            LOGGER.info("Old Signature: " + old_signature_hash)
            LOGGER.info(str(new_permission_document))
            LOGGER.info("new version: " + new_version)
            LOGGER.info("old version: " + old_version_ref)

            # Put the permission document if not exists yet
            # Need to compare signature data to not keeping on increasing versions
            response = client.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Item': {
                                'address': { 'S': address },
                                'version': { 'S': 'v' + new_version },
                                'id': { 'S': id },
                                'signature': { 'S': new_signature_hash },
                                'permission_document': python_obj_to_dynamo_obj(new_permission_document_obj).get('permission_document') 
                            },
                            'ConditionExpression': 'attribute_not_exists(address) AND attribute_not_exists(version)'
                        }
                    },
                    # Update the LATEST version of the permission document with the new permission document info and version_ref
                    {
                        'Update': {
                            'TableName': DYNAMO_DB_TABLE_NAME,
                            'Key': {
                                'address': { 'S': address },
                                'version': { 'S': 'LATEST' },
                            },
                            'ConditionExpression': '#version_ref = :old_version_ref',
                            'UpdateExpression': 'SET version_ref = version_ref + :incr, id = :id, signature = :signature, permission_document = :permission_document',
                            'ExpressionAttributeValues': {
                                ':incr': { 'N': '1' },
                                ':old_version_ref': { 'N': old_version_ref },
                                ':signature': { 'S': new_signature_hash },
                                ':permission_document': python_obj_to_dynamo_obj(new_permission_document_obj).get('permission_document'),
                                ':id': { 'S': id + "_LATEST"},
                            },
                            'ExpressionAttributeNames':{
                                '#version_ref': 'version_ref'
                            },
                        }
                    }
                ]
            )
    except PermissionDocumentNotChangedException as err:
        LOGGER.info("PermissionDocumentNotChangedException Unexpected error: %s" % err) 
        
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)



if __name__ == "__main__":
    main()


