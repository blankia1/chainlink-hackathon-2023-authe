import React, { ComponentProps, useEffect } from "react";
// import {
//     useDataGrid,
//     EditButton,
//     ShowButton,
//     MarkdownField,
//     List,
//     TagField,
// } from "@refinedev/mui";
// import { DataGrid, GridColumns, GridRowHeightParams, GridToolbar, GridActionsCellItem, GridValueFormatterParams } from "@mui/x-data-grid";
// import { useMany } from "@refinedev/core";
// import {
//     Button,
//     TextField,
//     Stack,
//     Toolbar,
//     Typography,
//     MenuItem,
//     Box,
//     TableContainer,
//     Table,
//     TableHead,
//     TableRow,
//     TableCell,
//     Checkbox,
//     CheckboxProps,
//     TableBody,
//     TableSortLabel,
//     TablePagination,
// } from "@mui/material";

// import { useAccount } from 'wagmi'

// export const PermissionDocumentList = () => {
//     const { address, isConnected } = useAccount()

//     const { dataGridProps } = useDataGrid();
//     // const { data: categoryData, isLoading: categoryIsLoading } = useOne({
//     //     resource: "public/GET/v0/permission/documents?address=0x71C7656EC7ab88b098defB751B7401B5f6d8976F&version=ALL",
//     //     meta: {
//     //         headers: {
//     //             "x-custom-header": "hello world",
//     //         },
//     //     }
//     // });

//     const addresses = ["0x560EcF1541389d71484374CFeb750847525582be", "0xca8fa8f0b631ecdb18cda619c4fc9d197c8affca"];

//     const { data: categoryData, isLoading: categoryIsLoading } = useMany({
//         resource: "permission-documents",
//         meta: {"address": "0x560EcF1541389d71484374CFeb750847525582be", "version": "ALL"},
//         ids: addresses,
//         // queryOptions: {
//         //     enabled: !!dataGridProps?.rows,
//         // },
        
//     });

//     // const { data: categoryData, isLoading: categoryIsLoading } = useMany({
//     //     resource: "public/GET/v0/permission/documents",
//     //     ids: dataGridProps?.rows?.map((item: any) => item?.address) ?? [],
//     //     queryOptions: {
//     //         enabled: !!dataGridProps?.rows,
//     //     },
        
//     // });

//     const columns = React.useMemo<GridColumns<any>>(
//         () => [
//             {
//                 field: "id",
//                 headerName: "id",
//                 headerAlign: "left",
//                 align: "left",
//             },
//             {
//                 field: "address",
//                 headerName: "Address",
//                 headerAlign: "left",
//                 enableColumnResizing: true,
//                 minWidth: 200,
//                 align: "left",
//                 flex: 0.5,
//             },
//             {
//                 field: "version",
//                 headerName: "Version",
//                 headerAlign: "left",
//                 align: "left",
//                 minWidth: 25,
//             },
//             {
//                 field: "signature",
//                 headerName: "Signature",
//                 flex: 0.5,
//                 minWidth: 100,
//                 renderCell: function render({ value, row }) {
//                     return (
//                         // <Stack word-wrap="break-word">
//                         //     <MarkdownField 
//                         //         value={(row.permission_document.Signature ?? "").slice(0, 25) + "..."}
//                         //     />
//                         // </Stack>
//                         <Stack word-wrap="break-word">
//                             <MarkdownField 
//                                 value={(row.signature ?? "").slice(0, 25) + "..."}
//                             />
//                         </Stack>
//                     );
//                 },
//             },
//             {
//                 field: "status",
//                 headerName: "Status",
//                 renderCell: function render({ row }) {
//                     let color: ComponentProps<typeof TagField>["color"];
//                     switch (row.status) {
//                         case "published":
//                             color = "success";
//                             break;
//                         case "rejected":
//                             color = "error";
//                             break;
//                         case "draft":
//                             color = "info";
//                             break;
//                         default:
//                             color = "success"; // "default"
//                             break;
//                     }
//                     return <TagField value={row.status ?? "published"} color={color} />;
//                 },
//                 minWidth: 120,
//                 flex: 0.3,
//             },
//             {
//                 field: "actions",
//                 headerName: "Actions",
//                 sortable: false,
//                 renderCell: function render({ row }) {                    
//                     if (row.version === "LATEST") {
//                         return (
//                             <>
//                                 <EditButton hideText recordItemId={row.id} />
//                                 <ShowButton hideText recordItemId={row.id} />
//                             </>
//                         );
//                     }
//                     else{
//                         return (
//                             <>
//                             <ShowButton hideText recordItemId={row.id} />
//                             </>
//                         );
//                     }
//                 },
//                 align: "center",
//                 headerAlign: "center",
//                 minWidth: 80,
//             },
//         ],
//         [categoryData?.data],
//     );

    
//     return (
//         <List>
//             <DataGrid 
//                 {...dataGridProps} 
//                 columns={columns} 
//                 autoHeight 
//                 // sx={{ overflow: "wrap", style: { 'whiteSpace': 'unset', overflowWrap: "break-word" } }}
//                 // style={{overflow:'wrap'}}
//                 // getRowHeight={({ id, densityFactor }: GridRowHeightParams) => {
//                 //     if ((id as number) % 2 === 0) {
//                 //       return 100 * densityFactor;
//                 //     }
                    
//                 //     return null;
//                 //   }}
//                 getRowHeight={() => 'auto'} 
//                 components={{
//                     Toolbar: GridToolbar,
//                 }}
//                 getRowId={(row) => row.id}
//                 />
//         </List>
//     );

           
// };


