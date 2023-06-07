import React, { useState } from "react";
import { IResourceComponentsProps } from "@refinedev/core";

import { DeleteButton, SaveButton, Edit, useForm } from "@refinedev/antd";

import { Button, Form, Input, Select } from "antd";

import { IPermissionDocument } from "interfaces";

import { useSignMessage } from 'wagmi'

export const PermissionDocumentEdit: React.FC<IResourceComponentsProps> = () => {
    const { data, error, isLoading, signMessage, variables } = useSignMessage()

    const { formProps, saveButtonProps, queryResult, onFinish } = useForm<IPermissionDocument>();

    const postData = queryResult?.data?.data;

    // const { selectProps: categorySelectProps } = useSelect<IPermissionDocumentStatement>({
    //     resource: "categories",
    //     defaultValue: postData?.id,
    // });

    // const { selectProps: tagsSelectProps } = useSelect<IPermissionDocument>({
    //     resource: "tags",
    //     defaultValue: postData?.permission_document.Signature,
    // });
      


    const onFinishHandler = (values : any ) => {
        // If no signature in permission document statement then add Signature: "" as placeholder so that it will be accepted by the api
        var permission_document = JSON.parse(values.permission_document)
        var signature

        if (data){
            permission_document.Signature = data
            signature = data
        }
        else if (permission_document.Signature.startsWith("0x")){
            signature = permission_document.Signature
        }
        else{
            permission_document.Signature = "unsigned"
            signature = "unsigned"
        }

        try {
            onFinish?.({
                address: `${values.address}`,
                chain: `${values.chain}`,
                signature: `${signature}`,
                status: `${values.status}`,
                version: `${values.version}`,
                permission_document: permission_document,
            });
        } catch (error) {
            console.error("Something bad happened");
            console.error(error);
        }

        // onFinish(values);
        // close();
        // return
    };

    async function SignMessage() {
        const message =  "Hello world"

        if (!permissionDocument) {
            // strip out the Signature keys
            var newPermissionDocument = {
                Version: queryResult?.data?.data.permission_document.Version,
                Statement: queryResult?.data?.data.permission_document.Statement
            }
            const signature = await signMessage({
                message: JSON.stringify(newPermissionDocument, null, 2),
              })
        } else{

            const signature = await signMessage({
                message: JSON.stringify(JSON.parse(permissionDocument), null, 2) // reformat the json
              })
        }
      }

    const [permissionDocument, setPermissionDocument] = useState('');
    const handleChange = (event : any) => {

        try {
            const obj = event
            setPermissionDocument(obj)

        } catch (error) {
            console.error("handleChange -> No valid json in permission document");
            console.error(error);
            return true
        }
      };

    return (
        <Edit saveButtonProps={{ ...saveButtonProps }} canDelete={postData?.status?.includes("draft")} footerButtons={({ saveButtonProps, deleteButtonProps }) => (
            <>
                <Button type="primary" onClick={SignMessage} 
                    >Sign the Permission Document
                </Button>
                <SaveButton {...saveButtonProps} />
                {deleteButtonProps && (
                    <DeleteButton {...deleteButtonProps} />
                )}
            </>
        )}
        >
            <Form {...formProps} onFinish={onFinishHandler} layout="vertical"   
                fields={[
                    {
                    name: ["permission_document"],
                    value: JSON.stringify(queryResult?.data?.data.permission_document, null, 2),
                },
            ]}>
                <Form.Item 
                        label="Address"
                        name="address"
                        rules={[
                            {
                                required: true,
                            },
                        ]}
                    >
                        <Input disabled={true} />
                </Form.Item>
                <Form.Item
                    label="Version"
                    name="version"
                    
                            
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                    >
                    <Input
                    // This is where you want to disable your UI control
                    disabled={true}
                    placeholder="Version"
                    />
                </Form.Item>
                <Form.Item
                    label="Status"
                    name="status"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Select
                        options={[
                            {
                                label: "Publish",
                                value: "published",
                            },
                            {
                                label: "Draft",
                                value: "draft",
                            },
                            {
                                label: "Reject",
                                value: "rejected",
                            },
                        ]}
                    />
                </Form.Item>
                <Form.Item
                    label="Chain"
                    name="chain"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Select
                        options={[
                            // {
                            //     label: "Ethereum",
                            //     value: "ethereum",
                            // },
                            {
                                label: "Sepolia",
                                value: "sepolia",
                            },
                            // {
                            //     label: "Goerli",
                            //     value: "goerli",
                            // },
                        ]}
                    />
                </Form.Item>
                <Form.Item
                    label="Permission Document"
                    name="permission_document"                    
                    rules={[
                        {
                            required: true,
                        },
                        {
                            validator: async (_, value) => {
                                if (!value) return;
                                try{
                                    JSON.parse(value)
                                    // setPermissionDocument(JSON.stringify(value, null, 2)) // set value in state to later sign the message
                                    return Promise.resolve();
                                }
                                catch{
                                    return Promise.reject(
                                        new Error("'No valid JSON"),
                                    );
                                }
                            },
                        },
                    ]}
                >
                    {/* <div contenteditable="true">
                    <Tag color="magenta">magenta</Tag>
                    </div> */}

                     <pre >{JSON.stringify(queryResult?.data?.data.permission_document, null, 2)}</pre>
                    {/* <MDEditor  onChange={handleChange}  preview='edit' data-color-mode="light"> */}
                    {/* <MDEditor  onChange={handleChange}  preview='edit' data-color-mode="light">

                    </MDEditor> */}
                </Form.Item>
                <Form.Item 
                        label="Signature needs to go here before publishing a new version:"
                        name="new_signature"
                        // rules={[
                        //     {
                        //         required: true,
                        //     },
                        // ]}
                    >
                        {/* <div>
                        <Input disabled={true} value={data} defaultValue={data} placeholder="Needs a new signature because the Permission document changed"/>
                        </div> */}
                         { data ? <Input disabled={true} value={data} defaultValue={data} placeholder="Needs a new signature because the Permission document changed"/>: null }
                         <div></div>
                </Form.Item>   
            </Form>
        </Edit>


    );
};



