import React from "react";
import { IResourceComponentsProps } from "@refinedev/core";

import { DeleteButton, SaveButton, Edit, useForm } from "@refinedev/antd";

import { Form, Input, Select } from "antd";
const { TextArea } = Input;

import { IDispute } from "interfaces";

import { useSignMessage } from 'wagmi'

export const DisputeEdit: React.FC<IResourceComponentsProps> = () => {
    const { data, error, isLoading, signMessage, variables } = useSignMessage()

    const { formProps, saveButtonProps, queryResult, onFinish } = useForm<IDispute>();

    const postData = queryResult?.data?.data;

    return (
        <Edit saveButtonProps={{ ...saveButtonProps }} canDelete={postData?.status?.includes("draft")} footerButtons={({ saveButtonProps, deleteButtonProps }) => (
            <>
                <SaveButton {...saveButtonProps} />
                {deleteButtonProps && (
                    <DeleteButton {...deleteButtonProps} />
                )}
            </>
        )}
        >
            <Form {...formProps} layout="vertical">
                <Form.Item
                    label="Id"
                    name="id"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input disabled={true} />
                </Form.Item>
                <Form.Item
                    label="Created At"
                    name="created_at"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input disabled={true} />
                </Form.Item>
                <Form.Item 
                        label="Address"
                        name="created_by"
                        rules={[
                            {
                                required: true,
                            },
                        ]}
                    >
                        <Input disabled={true} />
                </Form.Item>  
            <Form.Item
                    label="Transaction Hash"
                    name="transaction_hash"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input disabled={true} />
                </Form.Item>
                <Form.Item
                    label="Status"
                    name="status"
                    initialValue = "draft"
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
                    initialValue = "sepolia"
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
                    label="Action"
                    name="action"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Select disabled={true}
                        options={[
                            {
                                label: "Transfer",
                                value: "Transfer",
                            },
                            {
                                label: "TransferFrom",
                                value: "transferFrom",
                            },
                            {
                                label: "Approve",
                                value: "approve",
                            },
                            {
                                label: "Allowance",
                                value: "allowance",
                            },
                            {
                                label: "Mint",
                                value: "mint",
                            },
                        ]}
                    />
                </Form.Item>
                <Form.Item
                    label="Encoded Input Data"
                    name="encoded_input_data"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <TextArea
                        autoSize={{ minRows: 5, maxRows: 400 }}
                        disabled={true}
                    />
                </Form.Item>
                <Form.Item
                    label="Decoded Input Data"
                    name="decoded_input_data"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <TextArea
                        autoSize={{ minRows: 5, maxRows: 400 }}
                        disabled={true}
                    />
                </Form.Item>
                <Form.Item
                    label="Contract ABI"
                    name="contract_abi"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <TextArea
                        placeholder="ABI"
                        autoSize={{ minRows: 5, maxRows: 400 }}
                        disabled={true}
                    />
                </Form.Item>
                <Form.Item
                    label="Function ABI"
                    name="function_abi"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <TextArea
                        placeholder="ABI"
                        autoSize={{ minRows: 5, maxRows: 400 }}
                        disabled={true}
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
                    <TextArea
                        placeholder="Permission Document"
                        autoSize={{ minRows: 5, maxRows: 400 }}
                        disabled={true}
                    />
                </Form.Item>
                {/* <Form.Item label="Proof hash result"
                    name="proof_hash_result"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                    >
                    <Input placeholder="Proof hash result" disabled={true} />
                </Form.Item> */}
                <Form.Item label="Notes"
                    name="notes"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <TextArea
                        placeholder="Notes"
                        autoSize={{ minRows: 2, maxRows: 6 }}
                    />
                </Form.Item>
            </Form>
        </Edit>

    );
};



