import pytest
import os
import sys
import json
import logging
import boto3
import responses
import requests
from responses import matchers
import time
import uuid

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


id = uuid.uuid4().hex

example_unconfirmed_stream_transaction = {
	"confirmed": False,
	"chainId": "0xaa36a7",
	"abi": [{
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkCancelled",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkFulfilled",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkRequested",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "requestId",
			"type": "bytes32"
		}, {
			"indexed": True,
			"internalType": "bytes",
			"name": "data",
			"type": "bytes"
		}],
		"name": "RequestFulfilled",
		"type": "event"
	}],
	"streamId": "a892224b-ed66-4317-9301-dc01a272af00",
	"tag": "demo",
	"retries": 0,
	"block": {
		"number": "3561457",
		"hash": "0x2858ce3384f71288f6c03a3d2c31c6d874c9133aee471f18427845cded59f192",
		"timestamp": "1685085528"
	},
	"logs": [],
	"txs": [{
		"hash": id, # insert with unique hash
		"gas": "33086",
		"gasPrice": "1500000010",
		"nonce": "264",
		"input": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000",
		"transactionIndex": "56",
		"fromAddress": "0x78cf1d91c94667a4a6615829e394c9cce58fec9e",
		"toAddress": "0x0d84b1a4a01ea753cf7a58061010ec69bd484d47",
		"value": "0",
		"type": "2",
		"v": "1",
		"r": "68623677568783239942890942037904486350924283675994943669472078826599409570736",
		"s": "46220654584388056924474479272221784186174141546940106925291713539677290590337",
		"receiptCumulativeGasUsed": "10313961",
		"receiptGasUsed": "30926",
		"receiptContractAddress": 'null',
		"receiptRoot": 'null',
		"receiptStatus": "1"
	}],
	"txsInternal": [],
	"erc20Transfers": [],
	"erc20Approvals": [],
	"nftTokenApprovals": [],
	"nftApprovals": {
		"ERC721": [],
		"ERC1155": []
	},
	"nftTransfers": [],
	"nativeBalances": []
}

example_confirmed_stream_transaction = {
	"confirmed": True,
	"chainId": "0xaa36a7",
	"abi": [{
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkCancelled",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkFulfilled",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "id",
			"type": "bytes32"
		}],
		"name": "ChainlinkRequested",
		"type": "event"
	}, {
		"anonymous": False,
		"inputs": [{
			"indexed": True,
			"internalType": "bytes32",
			"name": "requestId",
			"type": "bytes32"
		}, {
			"indexed": True,
			"internalType": "bytes",
			"name": "data",
			"type": "bytes"
		}],
		"name": "RequestFulfilled",
		"type": "event"
	}],
	"streamId": "a892224b-ed66-4317-9301-dc01a272af00",
	"tag": "demo",
	"retries": 0,
	"block": {
		"number": "3561457",
		"hash": "0x2858ce3384f71288f6c03a3d2c31c6d874c9133aee471f18427845cded59f192",
		"timestamp": "1685085528"
	},
	"logs": [],
	"txs": [{
		"hash": id, # insert with unique hash
		"gas": "33086",
		"gasPrice": "1500000010",
		"nonce": "264",
		"input": "0x877f282b0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000",
		"transactionIndex": "56",
		"fromAddress": "0x78cf1d91c94667a4a6615829e394c9cce58fec9e",
		"toAddress": "0x0d84b1a4a01ea753cf7a58061010ec69bd484d47",
		"value": "0",
		"type": "2",
		"v": "1",
		"r": "68623677568783239942890942037904486350924283675994943669472078826599409570736",
		"s": "46220654584388056924474479272221784186174141546940106925291713539677290590337",
		"receiptCumulativeGasUsed": "10313961",
		"receiptGasUsed": "30926",
		"receiptContractAddress": 'null',
		"receiptRoot": 'null',
		"receiptStatus": "1"
	}],
	"txsInternal": [],
	"erc20Transfers": [],
	"erc20Approvals": [],
	"nftTokenApprovals": [],
	"nftApprovals": {
		"ERC721": [],
		"ERC1155": []
	},
	"nftTransfers": [],
	"nativeBalances": []
}

def test_process_streamed_unconfirmed_transactions_internal_lambda_handler(test_env_params):
    base_url = os.environ['BaseUrl']
	
    # Testing the process streamed transaction Lambda
    LOGGER.info('Testing the process streamed transaction Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/internal/ANY/v0/transactions/stream', json=example_unconfirmed_stream_transaction, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from process stream transaction Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 

    LOGGER.info("Sleeping for 5 seconds")
    time.sleep(5)

    LOGGER.info("hash is: " + str(id))
    LOGGER.info('Testing the get transactions Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions/' + id, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('is_confirmed')) == False

    
def test_process_streamed_confirmed_transactions_internal_lambda_handler(test_env_params):
    base_url = os.environ['BaseUrl']
	
    # Testing the process streamed transaction Lambda
    LOGGER.info('Testing the process streamed transaction Lambda')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
        response = requests.post(base_url + '/internal/ANY/v0/transactions/stream', json=example_confirmed_stream_transaction, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception("Error from process stream transaction Lambda", result)  
    except Exception as err:
        LOGGER.error("Unexpected error: %s" % err)

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 

    LOGGER.info("Sleeping for 5 seconds")
    time.sleep(5)

    LOGGER.info("hash is: " + str(id))
    LOGGER.info('Testing the get transactions Lambda')
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'Source-Platform': 'integration_test'}
    response = requests.get(base_url + '/public/GET/v0/transactions/' + id, headers=headers)
    result = response.json()

    LOGGER.info('Result')
    LOGGER.info(result)

    assert(response.status_code) == 200 
    assert(result.get('is_confirmed')) == True