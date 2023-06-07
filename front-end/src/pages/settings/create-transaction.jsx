import * as React from 'react'

import { usePrepareContractWrite, useContractWrite, erc20ABI } from 'wagmi'

export function CreateTransaction() {
//   const { data, error, isLoading, signMessage, variables } = useSignMessage()

  async function onClickFunction() {
    const message = "df"// formData.get('message')
    const result = await signMessage({ message })
  }

  const ABI = [
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_oracle",
          "type": "address"
        },
        {
          "internalType": "bytes32",
          "name": "_jobId",
          "type": "bytes32"
        },
        {
          "internalType": "uint256",
          "name": "_fee",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_link",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        }
      ],
      "name": "ChainlinkCancelled",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        }
      ],
      "name": "ChainlinkFulfilled",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "bytes32",
          "name": "id",
          "type": "bytes32"
        }
      ],
      "name": "ChainlinkRequested",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "string",
          "name": "information",
          "type": "string"
        }
      ],
      "name": "Information",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferRequested",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "internalType": "address",
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "to",
          "type": "address"
        }
      ],
      "name": "OwnershipTransferred",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "acceptOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "api_url",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes",
          "name": "_data",
          "type": "bytes"
        }
      ],
      "name": "convertCallDataToString",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "pure",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_data",
          "type": "bytes32"
        }
      ],
      "name": "convertHashToString",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "pure",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "requestId",
          "type": "bytes32"
        },
        {
          "internalType": "bytes",
          "name": "bytesData",
          "type": "bytes"
        }
      ],
      "name": "fulfillBytes",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "key",
          "type": "string"
        }
      ],
      "name": "getApprovedTransaction",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "hash_result",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes",
          "name": "buffer",
          "type": "bytes"
        }
      ],
      "name": "iToHex",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "pure",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_resource_address",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_functionName",
          "type": "string"
        },
        {
          "internalType": "bytes",
          "name": "_data",
          "type": "bytes"
        }
      ],
      "name": "requestAuthE",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_value",
          "type": "string"
        }
      ],
      "name": "setApiUrl",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "to",
          "type": "address"
        }
      ],
      "name": "transferOwnership",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "withdrawLink",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
  const { data, isLoading, isSuccess, write } = useContractWrite({
    address: '0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47',
    abi: erc20ABI,
    functionName: 'setApiUrl',
    args: 'https://api.authe.io/'
  })

//   const {
//     config,
//     error: prepareError,
//     isError: isPrepareError,
//   } = usePrepareContractWrite({
//     address: '0xfC6E622Bf36311c5BD376b26Bef307e78b40F247',
//     abi: ABI,
//     functionName: 'setApiUrl',
//     gasPrice: BigNumber.from(21000),
//     args: ['https://api.authe.io/'],
//     onSuccess(data) {
//         console.log("usePrepareContractWrite", "Success", "data", data);
//       },
//       onError(err) {
//         console.error("usePrepareContractWrite", err.message);
//       },
//   });

    // const { config } = usePrepareContractWrite({
    //     address: '0x40d7FF516A0105d304a7918f754215977097d768',
    //     abi: ABI,
    //     functionName: 'setApiBaseUrl',
    //     args: ['https://api.authe.io/public/GET/v0'],
    //     onSuccess(data) {
    //         console.log("usePrepareContractWrite", "Success", "data", data);
    //     },
    //     onError(err) {
    //         console.error("usePrepareContractWrite", err.message);
    //     },
    // })

//   const { config } = usePrepareContractWrite({
//     address: "0xfC6E622Bf36311c5BD376b26Bef307e78b40F247",
//     abi: ABI,
//     functionName: 'requestAuthE',
//     gasLimit: 50000000,
//     args: ["0x779877A7B0D9E8603169DdbD7836e478b4624789", "setApiUrl", "0xe8c75a300000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000003768747470733a2f2f30696f63676333706b362e657865637574652d6170692e75732d776573742d322e616d617a6f6e6177732e636f6d2f000000000000000000"],
//     onSuccess(data) {
//         console.log("usePrepareContractWrite", "Success", "data", data);
//       },
//     onError(err) {
//         console.error("usePrepareContractWrite", err.message);
//     },
//   })

// const { config } = usePrepareContractWrite({
//     address: "0x78Cf1D91C94667a4a6615829e394C9CCe58fEc9E",
//     abi: erc20ABI,
//     functionName: 'transfer',
//     gasLimit: 50000000,
//     args: ["0x78Cf1D91C94667a4a6615829e394C9CCe58fEc9E", '1' ],
//     onSuccess(data) {
//         console.log("usePrepareContractWrite", "Success", "data", data);
//       },
//     onError(err) {
//         console.error("usePrepareContractWrite", err.message);
//     },
//   })

//   const { config } = usePrepareContractWrite({
//     address: '0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47',
//     abi: erc20ABI,
//     functionName: 'transfer',
//     args: ['0x0D84b1A4A01ea753cf7a58061010ec69Bd484D47', '1'],
//     onSuccess(data) {
//         console.log("usePrepareContractWrite", "Success", "data", data);
//       },
//       onError(err) {
//         console.error("usePrepareContractWrite", err.message);
//       },
//   })


//   const { data, isLoading, isSuccess, write } = useContractWrite(config)

  
  return (
    <form
      // onSubmit={(event) => {
      //   event.preventDefault()
      //   const formData = new FormData(event.target)
      //   const message = "df"// formData.get('message')
      //   signMessage({ message })
      // }}
    >
    <div>
      <button onClick={() => write()}>Feed</button>
      {isLoading && <div>Check Wallet</div>}
      {isSuccess && <div>Transaction: {JSON.stringify(data)}</div>}
    </div>
 
      {data && (
        <div>
          {/* <div>Recovered Address: {recoveredAddress.current}</div> */}
          <div>Signature: {data}</div>
        </div>
      )}
     </form>
  )
}