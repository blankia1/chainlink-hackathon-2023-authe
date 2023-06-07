import os
import json
import logging
from moralis import evm_api
import boto3
import botocore
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    region = os.environ['Region']
    DYNAMO_DB_TABLE_NAME = os.environ['TransactionsDynamoDBTableName']

    MoralisApiKey = os.environ['Key2']

    if 'multiValueQueryStringParameters' in event:
        addresses =  event['multiValueQueryStringParameters'].get('address')
        chain =  event['queryStringParameters'].get('chain', 'sepolia')
    else:
        addresses = event.get('address', ['0x560ecf1541389d71484374cfeb750847525582be'])
        chain =  event.get('chain', 'sepolia')

    LOGGER.info(addresses)
    LOGGER.info("Addresses given are: {}".format(' '.join(map(str, addresses))))

    for address in addresses:
        
        params = {
            "address": address,
            "chain": chain,
        }

        LOGGER.info(params)
        LOGGER.info("Getting the transactions from Moralis")
        
        response = evm_api.transaction.get_wallet_transactions(
            api_key=MoralisApiKey,
            params=params,
        )

        transactions = response['result']
        LOGGER.info("Got number of transactions from Moralis: " + str(len(transactions)))

        dynamodb = boto3.resource('dynamodb',region_name=region)

        if len(transactions) > 0:
            LOGGER.info("Adding the transactions to the DB")

            for transaction in transactions:
                LOGGER.info("Adding the transaction to the DB")
                LOGGER.info("Address: " + address) 
                LOGGER.info("Hash: " + transaction.get("hash")) 
                LOGGER.info("Chain: " + chain) 

                try:
                    table = dynamodb.Table(DYNAMO_DB_TABLE_NAME)
                    response = table.put_item(
                    Item={
                            "address": address, # Custom added
                            "hash": transaction.get("hash"),
                            "chain": chain, # Custom added
                            "transaction": transaction
                        },
                    ConditionExpression='attribute_not_exists(#hash)',
                    ExpressionAttributeNames={"#hash": "hash"}
                    )
                except botocore.exceptions.ClientError as err:
                    # Ignore the ConditionalCheckFailedException
                    if err.response['Error']['Code'] != 'ConditionalCheckFailedException':
                        LOGGER.warn("The transaction already exists in the DB: %s" % err)
                except Exception as err:
                    LOGGER.error("Unexpected error: %s" % err)
                    raise

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success"}),

        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }
