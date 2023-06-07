import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { IResourceComponentsProps } from "@refinedev/core";

import {
    List,
    useTable,
    DateField,
    TagField,
    EditButton,
    ShowButton,
} from "@refinedev/antd";
import dayjs from "dayjs";
import { Table, Space } from "antd";

import { IDispute } from "interfaces";
import { useAccount } from 'wagmi'


export const DisputeList: React.FC<IResourceComponentsProps> = () => {
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

    const { tableProps, sorter } = useTable<IDispute>({
        meta:{"address": address, "chain": "sepolia"}
    });

    return (
        <List>
            <Table {...tableProps} rowKey="id">
                <Table.Column<IDispute>
                    title="Id" 
                    dataIndex="id" 
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.id.substring(0, 10)
                                }` }
                            />
                        );
                    }}
                />
                <Table.Column<IDispute>
                    title="Transaction Hash" 
                    dataIndex="transaction_hash" 
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.transaction_hash.substring(0, 10)
                                }` }
                            />
                        );
                    }}
                />
                <Table.Column<IDispute>
                    title="Status"
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.status  === "published" ? "published" : record?.status 
                                }` }
                                color={  record?.status  === "published" ? "green" : ""}
                            />
                        );
                    }}
                />   
                <Table.Column
                    dataIndex="created_at"
                    title="Created At"
                    key="created_at"
                    render={(value) => <DateField value={dayjs.unix(value)} format="LLL"></DateField>}
                />     
                <Table.Column<IDispute>
                    title="Actions"
                    dataIndex="actions"
                    render={(_, record) => (
                        <Space>
                            <EditButton
                                hideText
                                size="small"
                                recordItemId={record.id}
                            />
                            <ShowButton
                                hideText
                                size="small"
                                recordItemId={record.id}
                            />
                        </Space>
                    )}
                />   
            </Table>
        </List>
    );
};
