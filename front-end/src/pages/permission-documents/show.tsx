import React, { useState } from "react";
import { useShow, IResourceComponentsProps, useOne } from "@refinedev/core";

import { TagField, Show } from "@refinedev/antd";

import { Button, Typography } from "antd";

import { IPermissionDocument } from "interfaces";
import { recoverMessageAddress } from 'viem'
import type { Hex } from 'viem'

const { Title, Text } = Typography;

export const PermissionDocumentShow: React.FC<IResourceComponentsProps> = () => {
    const { queryResult } = useShow<IPermissionDocument>();
    const { data, isLoading } = queryResult;
    const record = data?.data;

    const { data: categoryData, isLoading: categoryIsLoading } =
        useOne<IPermissionDocument>({
            resource: "permission-documents-show",
            id: record?.id || "",
            queryOptions: {
                enabled: !!record,
            },
            meta: {"address": record?.address}
        });

    
    const [recoveredAddress, setRecoveredAddress] = useState('');

    async function OnClick(){
        console.log("handle change")
        if (!data?.data.permission_document || !data?.data.signature) {
        } else{

            // strip out the signature key
            var newPermissionDocument = {
                Version:data?.data.permission_document.Version,
                Statement: data?.data.permission_document.Statement
            }

            if(newPermissionDocument && data?.data.signature && data?.data.permission_document.Signature && data?.data.permission_document.Signature != "unsigned" ){
                const recoveredAddress = await recoverMessageAddress({
                    message: JSON.stringify(newPermissionDocument, null, 2),
                    signature: data?.data.permission_document.Signature as Hex,
                    })
                setRecoveredAddress(recoveredAddress)
            }
        }
    };

    React.useEffect(() => {
        ;(async () => {
            if (!isLoading) {    
                // strip out the signature key
                var newPermissionDocument = {
                    Version:data?.data.permission_document.Version,
                    Statement: data?.data.permission_document.Statement
                }
    
                if(newPermissionDocument && data?.data.signature && data?.data.permission_document.Signature && data?.data.permission_document.Signature != "unsigned" ){
                    const recoveredAddress = await recoverMessageAddress({
                        message: JSON.stringify(newPermissionDocument, null, 2),
                        signature: data?.data.permission_document.Signature as Hex,
                        })
                    setRecoveredAddress(recoveredAddress)
                }
            }
        })()
      }, [])

    return (
        <Show isLoading={isLoading}>
            <Title level={5}>Id</Title>
            <Text>{record?.id}</Text>

            <Title level={5}>Address</Title>
            <Text>{record?.address}</Text>

            <Title level={5}>Version</Title>
            <Text>
                {categoryIsLoading ? "Loading..." : categoryData?.data.version}
            </Text>

            <Title level={5}>Version Ref</Title>
            <Text>
             {categoryIsLoading ? "Loading..." : categoryData?.data.version_ref} 
            </Text>
            <Title level={5}>Permission Document</Title>
            <Text>
            <pre>{categoryIsLoading ? "Loading..." : JSON.stringify(categoryData?.data.permission_document, null, 2)}</pre>
            </Text>
            <Title level={5}>Is Verified document</Title>
            <Text>
                {categoryIsLoading ? "Loading..." : <TagField value={recoveredAddress} color={"success"} />}
            </Text>
            
            <Button type="primary" onClick={OnClick} 
                    >Verify the Signature
            </Button>
        </Show>
    );
};
