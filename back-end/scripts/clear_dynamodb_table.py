import os
import json
import logging
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

ENVIRONMENT_PARAMETERS_PATH = '../src/tests/test.env.json'


def test_env_params():
    """Load environment variables to mock"""
    data = {}
    with open(ENVIRONMENT_PARAMETERS_PATH) as json_file:
        data = json.load(json_file)
    for (k, v) in data["Parameters"].items():
        os.environ[k] = str(v)
    return data



def main():
    LOGGER.info("Getting items from Dynamodb")
    test_env_params()
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['PermissionDocumentsDynamoDBTableName']
    client = boto3.client('dynamodb', region)

    response = client.scan(TableName = DYNAMO_DB_TABLE_NAME)
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    LOGGER.info("Found all items from Dynamodb")

    # The list of items to delete
    items_to_delete = [
        # {key_name: {'S': 'item1'}},
        # {key_name: {'S': 'item2'}},
        # {key_name: {'S': 'item3'}},
    ]

    for item in data:
        parsed_item = dynamo_obj_to_python_obj(item) 
    
        address = parsed_item['address']
        version = parsed_item['version']
        item = python_obj_to_dynamo_obj({
            'address': address, 
            'version': version
            })
        items_to_delete.append(item)
        
    LOGGER.info("Deleting items:")
    # LOGGER.info(items_to_delete)
    LOGGER.info("Number of items to delete:")
    LOGGER.info(len(items_to_delete))

    if len(items_to_delete) == 0:
        LOGGER.info("Nothing to delete")
        return
        
    # Prepare the request object for the batchWriteItem operation
    request = {
        'RequestItems': {
            DYNAMO_DB_TABLE_NAME: [
                {
                    'DeleteRequest': {
                        'Key': item
                    }
                } for item in items_to_delete
            ]
        }
    }

    # # Execute the batchWriteItem operation
    response = client.batch_write_item(**request)

    LOGGER.info("Finished deleting items")

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

if __name__ == "__main__":
    main()


