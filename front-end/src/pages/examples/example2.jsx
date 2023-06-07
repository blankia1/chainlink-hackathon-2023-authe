import React, { useEffect, useState } from 'react';

import { useNavigate } from 'react-router-dom';
import { Show } from "@refinedev/antd";
const { Title, Text } = Typography;
import { Typography } from "antd";
import axios from 'axios';
import { useBalance, useNetwork, useContractRead, usePrepareContractWrite, useContractWrite, erc20ABI } from 'wagmi'

import { useDebounce } from 'use-debounce'
// import { ethers } from "ethers";
import { utils } from "ethers";

export default function Example2() {
  const navigate = useNavigate();
  const autheProxyAddress = "0xe119db227ef4ca98e71c7b994af01e8cd8224b1d" //"0x4A01F50136B78C14A02d793BC2b0236864D9CA99";
  const customERC20ContractAddress = "0x795e84fbd078f8da21a840ea5ab0ec0fde6c3954" // "0xaFe39F6B68464223c49c457F94628D26173FF8B6";

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
      "name": "oracle_result",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
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
      "name": "requestApproval",
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


  const custom_ERC20_ABI =  [
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "total",
          "type": "uint256"
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
          "internalType": "address",
          "name": "tokenOwner",
          "type": "address"
        },
        {
          "indexed": true,
          "internalType": "address",
          "name": "spender",
          "type": "address"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "tokens",
          "type": "uint256"
        }
      ],
      "name": "Approval",
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
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "tokens",
          "type": "uint256"
        }
      ],
      "name": "Transfer",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "delegate",
          "type": "address"
        }
      ],
      "name": "allowance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "delegate",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "numTokens",
          "type": "uint256"
        }
      ],
      "name": "approve",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "tokenOwner",
          "type": "address"
        }
      ],
      "name": "balanceOf",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
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
      "inputs": [],
      "name": "decimals",
      "outputs": [
        {
          "internalType": "uint8",
          "name": "",
          "type": "uint8"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "getUseAuthProxy",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
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
      "name": "name",
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
          "internalType": "address",
          "name": "receiver",
          "type": "address"
        }
      ],
      "name": "requestTokensFromOwner",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "_value",
          "type": "string"
        }
      ],
      "name": "setApprovedTransaction",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "setUseAuthProxy",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "symbol",
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
      "name": "totalSupply",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "receiver",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "numTokens",
          "type": "uint256"
        }
      ],
      "name": "transfer",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "buyer",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "numTokens",
          "type": "uint256"
        }
      ],
      "name": "transferFrom",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

  const [to, setTo] = React.useState('')
  const [debouncedTo] = useDebounce(to, 500)
 
  const [userAddress, setUserAddress] = React.useState('')
  const [debouncedUserAddress] = useDebounce(userAddress, 500)

  const [amount, setAmount] = React.useState('')
  const [debouncedAmount] = useDebounce(amount ? utils.parseEther(amount) : '1', 500)
  
  const [encodedData, setEncodedData] = React.useState('')
  const [debouncedToEncodedData] = useDebounce(encodedData, 500)
  
  const [requestApprovalValidation, setRequestApprovalValidation] = React.useState('')


  // const { config } = usePrepareContractWrite({
  //   address: autheProxyAddress,
  //   abi: ABI,
  //   functionName: 'requestApproval',
  //   gasLimit: 500000000,
  //   args: [customERC20ContractAddress, "transfer", "0xa9059cbb000000000000000000000000560ecf1541389d71484374cfeb750847525582be000000000000000000000000000000000000000000000000000009184e72a000"],
  //   onSuccess(data) {
  //       console.log("usePrepareContractWrite", "Success", "data", data);
  //     },
  //   onError(err) {
  //       console.error("usePrepareContractWrite", err.message);
  //   },
  // })
  
  // const { config } = usePrepareSendTransaction({
  //   request: {
  //     to: debouncedTo,
  //     value: debouncedAmount ? utils.parseEther(debouncedAmount) : undefined,
  //   },
  // })

  const { config: set_auth_provider } = usePrepareContractWrite({
    address: customERC20ContractAddress,
    abi: custom_ERC20_ABI,
    functionName: 'setUseAuthProxy',
    gasLimit: 50000000,
    args: [autheProxyAddress],
    onSuccess(data) {
        console.log("EnableAuthEProvider", "Success", "data", data);
      },
    onError(err) {
        console.error("EnableAuthEProvider error", err.message);
    },
    watch: true,
  });

  const { config: config_request_approval } = usePrepareContractWrite({
      address: autheProxyAddress,
      abi: ABI,
      functionName: 'requestApproval',
      gasLimit: 50000000,
      args: [customERC20ContractAddress, "transfer", debouncedToEncodedData],
      onSuccess(data) {
          console.log("config_request_approval", "Success", "data", data, "real transfer data", encodedData);
        },
      onError(err) {
          console.error("config_request_approval error", err.message);
      },
  });

  const { config: send_real_transaction } = usePrepareContractWrite({
    address: customERC20ContractAddress,  
    abi: erc20ABI,
    functionName: 'transfer',
    gasLimit: 50000000,
    args: [debouncedTo, debouncedAmount],
    onSuccess(data) {
        console.log("sendRealTransaction", "Success", "data", data);
      },
    onError(err) {
        console.error("sendRealTransaction error", err.message);
    },
    watch: true,
});

const { config: request_custom_token } = usePrepareContractWrite({
  address: customERC20ContractAddress,  
  abi: custom_ERC20_ABI,
  functionName: 'requestTokensFromOwner',
  gasLimit: 50000000,
  args: [debouncedUserAddress], //'10000'
  onSuccess(data) {
      console.log("request_custom_token", "Success", "data", data, "user address: ", debouncedUserAddress);
    },
  onError(err) {
      console.error("request_custom_token error", err.message, "user address: ", debouncedUserAddress);
  },
  watch: true,
});

  const { data: data, isLoading: isLoading, isSuccess: isSuccess, write: setAuthProvider } = useContractWrite(set_auth_provider)
  const { data: data2, isLoading: isLoading2, isSuccess: isSuccess2, write: requestApproval } = useContractWrite(config_request_approval)
  const { data: data3, isLoading: isLoading3, isSuccess: isSuccess3, write: sendRealTransaction } = useContractWrite(send_real_transaction)
  const { data: data4, isLoading: isLoading4, isSuccess: isSuccess4, write: requestCustomToken } = useContractWrite(request_custom_token)

  const [session, setSession] = useState({});
  const { chain, chains } = useNetwork()

  useEffect(() => {
    axios(`${process.env.REACT_APP_SERVER_URL}/authenticate`, {
      withCredentials: true,
    })
      .then(({ data }) => {
        const { iat, ...authData } = data; // remove unimportant iat value

        setSession(authData);
      })
      .catch((err) => {
        navigate('/signin');
      });
  }, []);

  async function signOut() {
    await axios(`${process.env.REACT_APP_SERVER_URL}/logout`, {
      withCredentials: true,
    });
    setSession()
    navigate('/signin');
  }

  function OnClickRequestApproval(){
    console.log("Request approval on click clicked")
    if ({amount}?.amount && {to}?.to){
      setRequestApprovalValidation("")

      setEncodedData(encodeFunctionData({
        abi: erc20ABI,
        functionName: 'transfer',
        args: [debouncedTo, debouncedAmount]
      }))
      requestApproval?.()
    }
    else{
      setRequestApprovalValidation(true)
    }
  }

  function OnClickEnableAuthEProvider(){
    setAuthProvider?.()
  }

  function OnClickRequestCustomToken(){
    setUserAddress(session.address)
    requestCustomToken?.()
  }

  const { data: contract_read_data, isLoading: isLoadingRead, isSuccess: isSuccessRead, error: isErrorRead }  = useContractRead({
    address: customERC20ContractAddress,
    abi: custom_ERC20_ABI,
    functionName: 'getUseAuthProxy',
    args: [session.address],
    onSuccess(data) {
      console.log('Success contract_read_data', data, contract_read_data, session?.address)
    },
    onError(error) {
      console.log('Error contract_read_data', error, contract_read_data, session?.address)
    },
    watch: true,
  })
  
  const { data: dataBalanceOf, isSuccess: isSuccessBalanceOf, isError: isErrorBalanceOf, isLoading: isLoadingBalanceOf } = useBalance({
    address: session.address,
    token: customERC20ContractAddress,
    onSuccess(data) {
      console.log('Success dataBalanceOf', data, dataBalanceOf, session?.address)
    },
    onError(error) {
      console.log('Error dataBalanceOf', error, dataBalanceOf, session?.address)
    },
    watch: true,
  })

  return (
    <Show isLoading={isLoading}>
      <Title level={5}>Example 2 - Dispute an incorrect approval response</Title>
      <h3>User session:</h3>
      <pre>{JSON.stringify(session, null, 2)}</pre>
      <button type="button" onClick={signOut}>
        Sign out
      </button>

      <>
      {chain && <div>Connected to {chain.name}</div>}
      {chains && (
        <div>Available chains: {chains.map((chain) => chain.name)}</div>
      )}
    </>
    <br></br> 
    <br></br>
    <br></br>
    <Title level={5}>Prerequisite - Do all the steps from example 1.</Title>
    <Text> 
        Make sure that you have done all the steps from Example 1.
    </Text>

    <br></br> 
    <br></br>
    <br></br>
    <Title level={5}>Step 1 - Request an incorrect approval </Title>
    <Text> 
        By clicking this button the AuthE proxy will respond in an incorrect way. If a request needed to be approved, it will deny it and vice versa. So basically it inverts the response. 
        Afterwards you can can go to the transaction page and start a Dispute flow. How the dispute is handled can be customized in the smart contract. Maybe a slashing, maybe an insurance mechanise etc. 
    </Text>
    <br></br>
    <br></br>
    <div>
      </div>
      <button onClick={OnClickRequestApproval} disabled={isLoading}>
        {isLoading2 ? 'Check Wallet' : 'Request an incorrect approval via the AuthE proxy contact'}
        {isSuccess2 && <div>Transaction: {JSON.stringify(data2)}</div>}
      </button>
      <br></br>
    <br></br>
    <br></br>
    
    <Title level={5}> <a href="/transactions" target="_blank">See your transaction here and open the one that you just made</a></Title> 
  </Show>
    
    
  );
}