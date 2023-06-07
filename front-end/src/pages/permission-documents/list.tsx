import { IResourceComponentsProps } from "@refinedev/core";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

import {
    List,
    useTable,
    EditButton,
    ShowButton,
    TagField,
} from "@refinedev/antd";

import { Table, Space } from "antd";

import { IPermissionDocument } from "interfaces";

import { useAccount } from 'wagmi'


export const PermissionDocumentList: React.FC<IResourceComponentsProps> = () => {
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

    const { tableProps, sorter } = useTable<IPermissionDocument>({
        meta: {"address": address},
        initialFilter: [
            {
                field: "address",
                operator: "eq",
                value: {address}
            },
        ],
    });

    return (
        <List>
            <Table {...tableProps} rowKey="id">
                <Table.Column<IPermissionDocument>
                    dataIndex="version"
                    title="Version"  
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.version.substring(0, 10)
                                }` }
                                color={  record?.status  === "published" ? "green" : ""}
                            />
                        );
                    }}
                />
                {/* <Table.Column dataIndex="version_ref" title="Version Ref" /> */}
                {/* <Table.Column dataIndex="id" title="ID" /> */}
                <Table.Column dataIndex="address" title="Address" />
                {/* <Table.Column dataIndex="signature" title="Signature" /> */}
                <Table.Column<IPermissionDocument>
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
                    <Table.Column<IPermissionDocument>
                    title="Is Signed"
                    render={(_, record) => {
                        return (
                            <TagField
                                value={`${
                                    record?.signature.match( "0x" ) ? "Signed" : "Not signed"
                                }` }
                                color={  record?.signature.match( "0x" ) ? "green" : "red"}
                            />
                        );
                    }}
                />                   
                {/* <Table.Column
                    dataIndex={["category", "title"]}
                    title="Category"
                />
                <Table.Column
                    dataIndex="createdAt"
                    title="Created At"
                    key="createdAt"
                    sorter
                    defaultSortOrder={getDefaultSortOrder("createdAt", sorter)}
                    render={(value) => <DateField value={value} format="LLL" />}
                />*/}
                <Table.Column<IPermissionDocument>
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

// {
//     field: "status",
//     headerName: "Status",
//     renderCell: function render({ row }) {
//         let color: ComponentProps<typeof TagField>["color"];
//         switch (row.status) {
//             case "published":
//                 color = "success";
//                 break;
//             case "rejected":
//                 color = "error";
//                 break;
//             case "draft":
//                 color = "info";
//                 break;
//             default:
//                 color = "success"; // "default"
//                 break;
//         }
//         return <TagField value={row.status ?? "published"} color={color} />;
//     },
//     minWidth: 120,
//     flex: 0.3,
// },
// {
//     field: "actions",
//     headerName: "Actions",
//     sortable: false,
//     renderCell: function render({ row }) {                    
//         if (row.version === "LATEST") {
//             return (
//                 <>
//                     <EditButton hideText recordItemId={row.id} />
//                     <ShowButton hideText recordItemId={row.id} />
//                 </>
//             );
//         }
//         else{
//             return (
//                 <>
//                 <ShowButton hideText recordItemId={row.id} />
//                 </>
//             );
//         }
//     },
//     align: "center",
//     headerAlign: "center",
//     minWidth: 80,
// },
