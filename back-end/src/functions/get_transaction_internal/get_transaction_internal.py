import os
import json
import logging
from moralis import evm_api

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    region = os.environ['Region']
    MoralisApiKey = os.environ['Key2']

    if 'pathParameters' in event:
        transaction_hash = event['pathParameters'].get('transaction_hash')
        chain =  event['queryStringParameters'].get('chain', 'sepolia')
    else:
        transaction_hash = event.get('transaction_hash', '0xc3cc7e98293f79c090f90c4af0bf0f8999486dcbb3174031032e92c0b4ce4cb0')
        chain =  event.get('chain', 'sepolia')

    LOGGER.info(transaction_hash)
    LOGGER.info("transaction_hash given is: {}".format(transaction_hash))


    params = {
        "transaction_hash": "0xc3cc7e98293f79c090f90c4af0bf0f8999486dcbb3174031032e92c0b4ce4cb0",
        "chain": "eth",
    }

    LOGGER.info("Getting the transactions from Moralis")
    response = evm_api.transaction.get_transaction(
        api_key=MoralisApiKey,
        params=params,
    )

    transaction = response
    
    return {
        'statusCode': 200,
        'body': json.dumps(transaction),

        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }
