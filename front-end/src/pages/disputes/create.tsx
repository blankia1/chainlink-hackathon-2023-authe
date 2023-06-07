import { IResourceComponentsProps } from "@refinedev/core";
import { useAccount } from 'wagmi'

import {
    Create,
    useForm,
} from "@refinedev/antd";
const { TextArea } = Input;
import { Form, Input, Select } from "antd";

import { IDispute } from "interfaces";

export const DisputeCreate: React.FC<IResourceComponentsProps> = () => {
    const { address, isConnected } = useAccount()

    const { formProps, saveButtonProps, onFinish } = useForm<IDispute>();

    const onFinishHandler = (values : any ) => {
        
        // onFinish?.({
        //     address: `${values.address}`,
        //     chain: `${values.chain}`,
        //     signature: signature,
        //     status: `${values.status}`,
        //     version: `${values.version}`,
        //     permission_document: permission_document,
        // });

        onFinish(values);
        // close();
    };

    return (
        <Create saveButtonProps={{ ...saveButtonProps}} 
        >
            <Form {...formProps} onFinish={onFinishHandler} layout="vertical">
            <Form.Item
                    label="Address"
                    name="created_by"
                    initialValue={address}
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
                    initialValue="PUT_THE_TRANSACTION_HASH_HERE"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input disabled={false} />
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
                    label="Action"
                    name="action"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Select
                        options={[
                            {
                                label: "Transfer",
                                value: "transfer",
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
                    />
                </Form.Item>
                <Form.Item label="Proof hash result"
                    name="proof_hash_result"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                    >
                    <Input placeholder="Proof hash result" />
                </Form.Item>
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
        </Create>
    );
};
