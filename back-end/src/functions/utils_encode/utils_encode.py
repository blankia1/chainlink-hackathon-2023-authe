import os
import json
import logging
from web3 import Web3, EthereumTesterProvider
from eth_abi import encode

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    if event.get('body'):
        body = json.loads(event["body"])
        messages_to_encode = body['messages_to_encode']
    else:
        messages_to_encode = event['messages_to_encode']

    LOGGER.info("Received the following messages to encode: " + str(messages_to_encode))

    w3 = Web3(EthereumTesterProvider())

    types = []
    values = []
    for message_to_encode in messages_to_encode:
        LOGGER.info("Encoding the following message: " + str(message_to_encode))
        types += message_to_encode.keys()
        values += message_to_encode.values()

    encoded_data = encode(
        types,
        values
    )

    encoded_hash = w3.keccak(encoded_data).hex()
    LOGGER.info("Encoded hash: " + encoded_hash)

    LOGGER.info("Finished")
    return {
        'statusCode': 200,
        'body': json.dumps({"encoded_message": encoded_hash}),
    }

