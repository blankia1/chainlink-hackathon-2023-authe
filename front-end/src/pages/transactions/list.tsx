import React, { ComponentProps, useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

import { IResourceComponentsProps } from "@refinedev/core";

import {
    List,
    useTable,
    DateField,
    TagField,
    ShowButton,
} from "@refinedev/antd";
import dayjs from "dayjs";
import { Table, Space } from "antd";

import { ITransaction } from "interfaces";
import { useAccount } from 'wagmi'


export const TransactionsList: React.FC<IResourceComponentsProps> = () => {
    const { address, isConnected } = useAccount()
    const [session, setSession] = useState({});
    const navigate = useNavigate();
    
    useEffect(() => {
        axios(`${process.env.REACT_APP_SERVER_URL}/authenticate`, {
          withCredentials: true,
        })
          .then(({ data }) => {
            const { iat, ...authData } = data; // remove unimportant iat value
    
            setSession(authData);
          })
          .catch((err) => {
            console.log(err)
            navigate('/signin');
          });
      }, []);

    const { tableProps, sorter } = useTable<ITransaction>({
        meta:{"address": address, "chain": "sepolia"}
        // initialFilter: [
        //     {
        //         field: "address",
        //         operator: "eq",
        //         value: "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        //     },
        // ],
    });

    return (
        <List>
            <Table {...tableProps} rowKey="hash">
                <Table.Column<ITransaction>
                    title="Hash" 
                    dataIndex="hash" 
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.hash.substring(0, 10)
                                }` }
                            />
                        );
                    }}
                />
                {/* <Table.Column dataIndex="id" title="ID" /> */}
                <Table.Column dataIndex="address" title="Address" />
                <Table.Column
                    dataIndex="to_address"
                    title="To"
                    key="to_address"
                    render={(value) => {
                        // let value: ComponentProps<typeof TagField>["value"];
                        switch (value) {
                            case "0xe119db227ef4ca98e71c7b994af01e8cd8224b1d":
                                return "AuthE Proxy"
                            case "0x795e84fbd078f8da21a840ea5ab0ec0fde6c3954":
                                return "Custom ERC20 contract";
                            default:
                                return value
                        }
                    }}
                 />
                <Table.Column
                    dataIndex="resource_address"
                    title="Resource Address"
                    key="resource_address"
                    render={(value) => {
                        // let value: ComponentProps<typeof TagField>["value"];
                        switch (value) {
                            case "0xe119db227ef4ca98e71c7b994af01e8cd8224b1d":
                                value = "AuthE Proxy"
                                break;
                            case "0x795e84fbd078f8da21a840ea5ab0ec0fde6c3954":
                                value = "Custom ERC20 contract";
                                break;
                            default:
                                break;
                        }
                        return <TagField  value={value} />;
                    }}
                 />
                <Table.Column
                    dataIndex="decoded_input_function"
                    title="Action"
                    key="decoded_input_function"
                    render={(value) => {
                        switch (value) {
                            case "UNKNOWN":
                                value = "..."
                                break;
                            default:
                                break;
                        }
                        return <TagField  value={value} />;
                    }}
                 />
                <Table.Column
                    dataIndex="status"
                    title="Status"
                    key="status"
                    render={(value) => {
                        let color: ComponentProps<typeof TagField>["color"];
                        switch (value) {
                            case "success":
                                color = "success";
                                break;
                            case "approved":
                                color = "success";
                                break;
                            case "approval_executed":
                                color = "success";
                                break;
                            case "denied":
                                color = "error";
                                break;
                            case "error":
                                color = "error";
                                break;   
                            case "approval_requested":
                                break;
                            case "not_authe_provider":
                                color = "warning";
                                break;   
                            default:
                                break;
                        }
                        return <TagField value={value} color={color} />;
                    }}
                 />
                 <Table.Column
                    dataIndex="created_at"
                    title="Created At"
                    key="created_at"
                    render={(value) => <DateField value={dayjs.unix(value)} format="LLL"></DateField>}
                />      
                <Table.Column<ITransaction>
                    title="Show more"
                    dataIndex="show"
                    render={(_, record) => (
                        <Space>
                            <ShowButton
                                hideText
                                size="small"
                                recordItemId={record.hash}
                            />
                        </Space>
                    )}
                />      
            </Table>
        </List>
    );
};
