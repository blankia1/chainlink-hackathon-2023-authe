import React, { useState } from "react";

import { useShow, IResourceComponentsProps, useOne } from "@refinedev/core";

import { Show } from "@refinedev/antd";

import { Button, Typography } from "antd";

import { IDispute } from "interfaces";

const { Title, Text } = Typography;

import { useBalance, useNetwork, useContractRead, usePrepareContractWrite, useContractWrite, erc20ABI } from 'wagmi'

import { useDebounce } from 'use-debounce'
// import { ethers } from "ethers";
import { utils } from "ethers";

import { encodeFunctionData } from 'viem'

export const DisputeShow: React.FC<IResourceComponentsProps> = () => {
    const { queryResult } = useShow<IDispute>();
    const { data, isLoading } = queryResult;
    const record = data?.data;

    const autheProxyAddress = "0xe119db227ef4ca98e71c7b994af01e8cd8224b1d" // "0xC209406e460cB85e2980e8cE5018AA1401b0bcB4";

    const ABI = [
        {
            "inputs": [
              {
                "internalType": "string",
                "name": "source",
                "type": "string"
              },
              {
                "internalType": "bytes",
                "name": "secrets",
                "type": "bytes"
              },
              {
                "internalType": "string[]",
                "name": "args",
                "type": "string[]"
              },
              {
                "internalType": "uint64",
                "name": "subscriptionId",
                "type": "uint64"
              },
              {
                "internalType": "uint32",
                "name": "gasLimit",
                "type": "uint32"
              }
            ],
            "name": "executeRequest",
            "outputs": [
              {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
              }
            ],
            "stateMutability": "nonpayable",
            "type": "function"
          },
        {
            "inputs": [],
            "name": "latestResponse",
            "outputs": [
              {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
              }
            ],
            "stateMutability": "view",
            "type": "function"
          },
      ]

      var source_api = `// Test validate permissions with api call
      // Retrieves a signed permission document from the API
      // Recalculates the approved action and returns the result
      // TODO Needs to check signatures 
      console.log("Test validate permissions with api")
      const dispute_id = args[2];
      const api_url = "https://api.authe.io/public/GET/v0/disputes/" + dispute_id
      
      const authEDisputeRequest = Functions.makeHttpRequest({
            url: api_url,
        })
      
      // First, execute all the API requests are executed concurrently, then wait for the responses
      const [authEDisputeResponse] = await Promise.all([
          authEDisputeRequest,
        ])
      
      if (!authEDisputeResponse.error) {
          console.log("Successfully retrieved the dispute from the API")
          // console.log(authEDisputeResponse)
      } else {
          console.log("autheDisputeRequest Error")
      }
      
      const action = authEDisputeResponse.data.action // args[i] // The action that was done by the user // Needs to be retrieved from the Blockchain so that it has not been tempered with
      const permission_document = JSON.parse(authEDisputeResponse.data.permission_document) // Needs to be compared with the result_proof_hash to check if it has not been tempered with
      
      result = 0 // 0 = Deny / 1 = Allow
      let i = 0
      
      // For the hackathon only check 'action' permissions to keep it simple
      while (i < permission_document.Statement.length) {
          // console.log(permission_document.Statement[i]);
          effect = permission_document.Statement[i].Effect
          if(effect == "Allow"){
              if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
                  result = 1 // Allow
                  console.log(action + " is allowed in this statement")
              }
          }
          else if (effect == "Deny"){
              if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
                  console.log(action + " is denied in this statement")
                  result = 0; // Deny
                  break;   
              }
          }
          else{
              console.log("Effect is unknown")
          }
      
          i++;
      }
      
      if(result == 1){
          console.log("Validation result is: Allowed")
      }
      else{
          console.log("Validation result is: Denied")
      }
      return Functions.encodeUint256(result) // 0 = Deny / 1 = Allow
      `

      var source_local = `// Test validate permissions locally without api call
      console.log("Test validate permissions without api")
      const action = "transfer" // args[i] // The action that was done by the user
      
      const permission_document = {
          "Version": "2023-05-11",
          "Statement": [
              {
                  "Resource": [
                      "*"
                  ],
                  "Effect": "Deny",
                  "Action": [
                      "*"
                  ],
                  "Principal": [
                      "*"
                  ],
                  "Sid": "AllowAllPermissions"
              },
              {
                  "Resource": [
                      "*"
                  ],
                  "Effect": "Deny",
                  "Action": [
                      "transfer", "mint", "transferFrom"
                  ],
                  "Principal": [
                      "*"
                  ],
                  "Sid": "AllowAllPermissions"
              }
          ],
          "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340"
      };
      
      result = 0 // 0 = Deny / 1 = Allow
      let i = 0
      
      // For the hackathon only check 'action' permissions to keep it simple
      while (i < permission_document.Statement.length) {
          // console.log(permission_document.Statement[i]);
          effect = permission_document.Statement[i].Effect
          if(effect == "Allow"){
              if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
                  result = 1 // Allow
                  console.log(action + " is allowed in this statement")
              }
          }
          else if (effect == "Deny"){
              if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
                  console.log(action + " is denied in this statement")
                  result = 0; // Deny
                  break;   
              }
          }
          else{
              console.log("Effect is unknown")
          }
      
          i++;
      }
      
      if(result == 1){
          console.log("Validation result is: Allowed")
      }
      else{
          console.log("Validation result is: Denied")
      }
      return Functions.encodeUint256(result) // 0 = Deny / 1 = Allow`;

    const { data: categoryData, isLoading: categoryIsLoading } =
        useOne<IDispute>({
            resource: "disputes",
            id: record?.id || "",
            queryOptions: {
                enabled: !!record,
            },
            meta: {"id": record?.id}
        });

        
    const { config: create_dispute } = usePrepareContractWrite({
        address: autheProxyAddress,
        abi: ABI,
        functionName: 'executeRequest',
        args: [source_api.toString(), [], [categoryData?.data.resource_address, categoryData?.data.encoded_input_data, categoryData?.data.id], 428, 100000],
        onSuccess(data) {
            console.log("create_dispute", "Success", "data", data);
            },
        onError(err) {
            console.error("create_dispute error", err.message);
        },
        });

    const { data: dispute_result, isLoading: isLoadingRead, isSuccess: isSuccessRead, error: isErrorRead }  = useContractRead({
        address: autheProxyAddress,
        abi: ABI,
        functionName: 'latestResponse',
        args: [],
        onSuccess(data) {
            console.log('Success contract_read_data', data, dispute_result)
        },
        onError(error) {
            console.log('Error contract_read_data', error, dispute_result)
        },
        watch: true,
        })

    const { data: dataDispute, isLoading: isLoadingDispute, isSuccess: isSuccessDispute, write: createDispute } = useContractWrite(create_dispute)

    const [disputeResult, setShowDisputeResult] = useState(false);
    async function SubmitDispute() {
        setShowDisputeResult(true)
        console.log("Submit dispute ")
        createDispute?.()
        console.log({dataDispute})

      }

    return (
        <Show isLoading={isLoading} footerButtons={() => (
            <>
            {record?.status != "published" ? "Status should be 'published' before it can be send to the Blockchain" : <Button disabled={isLoadingDispute} type="primary" onClick={SubmitDispute}
                    >
                {isLoadingDispute ? 'Check Wallet' : 'Submit the dispute on the Blockchain'}
                </Button>}
            </>
        )}
        >
            <Title level={5}>Id</Title>
            <Text>{record?.id}</Text>

            <Title level={5}>Transaction Hash</Title>
            <Text>{record?.transaction_hash}</Text>

            <Title level={5}>Address</Title>
            <Text>{record?.created_by}</Text>   

            <Title level={5}>Resource address</Title>
            <Text>{record?.resource_address}</Text> 

            <Title level={5}>Status</Title>
            <Text>{record?.status}</Text>   

            <Title level={5}>Chain</Title>
            <Text>{record?.chain}</Text>   

            <Title level={5}>function_abi</Title>
            <Text>{record?.function_abi}</Text>

            <Title level={5}>contract_abi</Title>
            <Text>{record?.contract_abi}</Text>   

            <Title level={5}>input data</Title>
            <Text>{record?.encoded_input_data}</Text>   

            <Title level={5}>message proof</Title>
            <Text>{record?.result_hash}</Text>   

            <Title level={5}>result proof</Title>
            <Text>{record?.proof_hash_result}</Text>   

            <Title level={5}>notes</Title>
            <Text>{record?.notes}</Text>  

            <Title level={5}>linked approval</Title>
            <Text><a href={`/transactions/show/${record?.linked_approval}`}> Linked approval request </a></Text>

            <Title level={5}>permission_document</Title>
            <Text>
            <pre>{categoryIsLoading ? "Loading..." : JSON.parse(JSON.stringify(categoryData?.data.permission_document, null, 0))}</pre>
            </Text> 

            {disputeResult && <div>Latest Dispute result: {JSON.stringify(dispute_result)}</div>}
        </Show>
    );
};
