import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import { useAccount } from 'wagmi'

import { useShow, IResourceComponentsProps, useOne } from "@refinedev/core";

import { TagField, Show } from "@refinedev/antd";

import { Button, Typography } from "antd";

import { ITransaction } from "interfaces";

const { Title, Text } = Typography;
import axios from 'axios';

import { recoverMessageAddress } from 'viem'
import type { Hex } from 'viem'

export const TransactionShow: React.FC<IResourceComponentsProps> = () => {
    const navigate = useNavigate();
    const { address, isConnected } = useAccount()

    const { queryResult } = useShow<ITransaction>();
    const { data, isLoading } = queryResult;
    const record = data?.data;

    const [recoveredAddress, setRecoveredAddress] = useState('');

    const { data: categoryData, isLoading: categoryIsLoading } =
        useOne<ITransaction>({
            resource: "transactions",
            id: record?.hash || "",
            queryOptions: {
                enabled: !!record,
            },
            meta: {"transaction_hash": record?.hash}
        });

    async function OnClick(){
        if (!queryResult?.data?.data.permission_documents_sender || !queryResult?.data?.data.permission_documents_sender.Signature) {
            console.log("No Permission document or Signature")
        } else{

            // strip out the signature key
            var newPermissionDocument = {
                Version:queryResult?.data?.data.permission_documents_sender.Version,
                Statement: queryResult?.data?.data.permission_documents_sender.Statement
            }

            if(newPermissionDocument && queryResult?.data?.data.permission_documents_sender.Signature && queryResult?.data?.data.permission_documents_sender.Signature != "unsigned" ){
                const recoveredAddress = await recoverMessageAddress({
                    message: JSON.stringify(newPermissionDocument, null, 2),
                    signature: queryResult?.data?.data.permission_documents_sender.Signature as Hex,
                    })
                setRecoveredAddress(recoveredAddress)
            }
        }
    };

    const [disabled, setDisabled] = useState(false);
    async function createDispute(){
        setDisabled(true)

        const dispute_obj = {
            "transaction_hash": queryResult?.data?.data.hash,
            "created_by": address,
            "resource_address": queryResult?.data?.data.resource_address,
            "chain": "sepolia",
            "action": queryResult?.data?.data.decoded_input_function, 
            "contract_abi": "CUSTOM_ERC20",
            "function_abi": queryResult?.data?.data.decoded_input_function,
            "status": "draft",
            "result_hash": queryResult?.data?.data.encode_message_hash,
            "proof_hash_result": queryResult?.data?.data.verified_encode_message_hash,
            "transaction_encoded_input_data": queryResult?.data?.data.transaction_encoded_input_data,
            "decoded_input_data": queryResult?.data?.data.decoded_input_data,
            "permission_document": JSON.stringify(queryResult?.data?.data.permission_documents_sender, null, 2),
            "notes": "automatically created",
            "linked_approval": queryResult?.data?.data.hash,
        }
        console.log(dispute_obj)
        async function createDraftDispute() {
            const apiUrl = "https://api.authe.io";
            console.log("Sending the request")
            const url = `${apiUrl}/private/ANY/v0/disputes`
            const { data, status } = await axios.post(
                url,
                JSON.stringify(dispute_obj)
              );
          
            console.log("Dispute draft created with id: " + data.id)
            navigate('/disputes/edit/' + data.id);
    
            return {
                data,
            };
        }

        createDraftDispute()
    };

    return (
        <Show isLoading={isLoading} footerButtons={({ }) => (
            <>
            {record?.status == "not_authe_provider" ? "Incorrect status for dispute" : <Button type="primary" disabled={disabled} onClick={createDispute}
                    >Dispute this transaction 
                </Button>}
            </>
        )}>
            <Title level={5}>Hash</Title>
            <Text>{record?.hash}</Text>

            <Title level={5}>Address</Title>
            <Text>{record?.address}</Text>   

            <Title level={5}>Status</Title>
            <Text>{record?.status}</Text>   

            <Title level={5}>Chain</Title>
            <Text>{record?.chain}</Text>   

            <Title level={5}>Extra info</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.transaction, null, 2)}</pre></Text>

            <Title level={5}>Action</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.decoded_input_function, null, 2)}</pre></Text>  

            <Title level={5}>Resource</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.resource_address, null, 2)}</pre></Text>  

            <Title level={5}>Encoded input data</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.encoded_data, null, 2)}</pre></Text>            
 
            <Title level={5}>Decoded input data</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.decoded_input_data, null, 2)}</pre></Text>            
 
            <Title level={5}>Input hash</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.encode_message_hash, null, 2)}</pre></Text>            
 
            <Title level={5}>Proof hash</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.verified_encode_message_hash, null, 2)}</pre></Text>           
 
            <Title level={5}>Permission document</Title>
            <Text><pre>{JSON.stringify(queryResult?.data?.data.permission_documents_sender, null, 2)}</pre></Text>    
            <Title level={5}>Is Verified document</Title>
            <Text>
                {categoryIsLoading ? "Loading..." : <TagField value={recoveredAddress} color={"success"} />}
            </Text>
            
            <Button type="primary" onClick={OnClick} 
                    >Verify the Signature
            </Button>


 {/*
            <Title level={5}>Version Ref</Title>
            <Text>
             {categoryIsLoading ? "Loading..." : categoryData?.data.version_ref} 
            </Text>
            <Title level={5}>Permission Document</Title>
            <Text>
            <pre>{categoryIsLoading ? "Loading..." : JSON.stringify(categoryData?.data.permission_document, null, 2) }</pre>
            </Text> */}
        </Show>
    );
};
