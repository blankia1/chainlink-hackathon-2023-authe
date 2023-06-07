import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { IResourceComponentsProps } from "@refinedev/core";
import { useAccount } from 'wagmi'

import {
    Create,
    useForm,
    SaveButton,
    useSelect,
} from "@refinedev/antd";
import { useSignMessage, useNetwork } from 'wagmi'

import { Button, Form, Input, Upload, Select } from "antd";

import MDEditor from "@uiw/react-md-editor";

import { IPost, ICategory, ITags, IPermissionDocument } from "interfaces";
import { normalizeFile } from "utility/normalize";

export const PermissionDocumentCreate: React.FC<IResourceComponentsProps> = () => {
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

    const { data, error, signMessage, variables } = useSignMessage()
    const { formProps, saveButtonProps, onFinish } = useForm<IPermissionDocument>();
    // const { selectProps: categorySelectProps } = useSelect<ICategory>({
    //     resource: "categories",
    // });

    // const { selectProps: tagsSelectProps } = useSelect<ITags>({
    //     resource: "tags",
    // });

    const onFinishHandler = (values : any ) => {
        // If no signature in permission document statement then add Signature: "" as placeholder so that it will be accepted by the api
        var permission_document = JSON.parse(values.permission_document)
        var signature

        if (data){
            permission_document.Signature = data
            signature = data
        }
        else{
            permission_document.Signature = "unsigned"
            signature = "unsigned"
        }
        
        onFinish?.({
            address: `${values.address}`,
            chain: `${values.chain}`,
            signature: signature,
            status: `${values.status}`,
            version: `${values.version}`,
            permission_document: permission_document,
        });

        // onFinish(values);
        // close();
    };

    const [permissionDocument, setPermissionDocument] = useState('');

    async function SignMessage() {

        if (!permissionDocument) {
            console.log("No permission document")
        } else{
            
            const signature = await signMessage({
                message: JSON.stringify(JSON.parse(permissionDocument), null, 2), // reformat the json
              })
        }
      }

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
        <Create saveButtonProps={{ ...saveButtonProps }} footerButtons={({ saveButtonProps }) => (
            <>
                <Button type="primary" onClick={SignMessage} 
                    >Sign the Permission Document
                </Button>
                <SaveButton {...saveButtonProps} />
            </>
        )}
        >
            <Form {...formProps} onFinish={onFinishHandler} layout="vertical">
                <Form.Item
                    label="Address"
                    name="address"
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
                {/* <Form.Item
                    label="Category"
                    name={["category", "id"]}
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Select {...categorySelectProps} />
                </Form.Item> */}
                {/* <Form.Item
                    label="Tags"
                    name="tags"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                    getValueProps={(tags?: { id: string }[]) => {
                        return { value: tags?.map((tag) => tag.id) };
                    }}
                    getValueFromEvent={(args: string[]) => {
                        return args.map((item) => ({
                            id: item,
                        }));
                    }}
                >
                    <Select mode="multiple" {...tagsSelectProps} />
                </Form.Item> */}
                {/* <Form.Item
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
                                label: "Published",
                                value: "published",
                            },
                            {
                                label: "Draft",
                                value: "draft",
                            },
                            {
                                label: "Rejected",
                                value: "rejected",
                            },
                        ]}
                    />
                </Form.Item> */}
                {/* <Form.Item
                    label="Permission document"
                    name="permission_document"
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                    <Input />
                </Form.Item> */}
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
                                    setPermissionDocument(value) // set value in state to later sign the message
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
                    {/* <MDEditor  onChange={handleChange}  preview='edit' data-color-mode="light"> */}
                    <MDEditor onChange={handleChange}  preview='edit' data-color-mode="light">

                    </MDEditor>
                </Form.Item>
                <Form.Item 
                        label="Signature needs to go here before publishing a new version:"
                        name="signature"
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
                </Form.Item>   
            </Form>
        </Create>
    );
};
