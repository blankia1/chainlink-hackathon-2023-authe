import React from "react";
import { IResourceComponentsProps } from "@refinedev/core";

import { Edit, useForm } from "@refinedev/antd";

import { Form } from "antd";
import MDEditor from "@uiw/react-md-editor";

import { IPermissionDocument } from "interfaces";
export const PermissionDocumentEdit: React.FC<IResourceComponentsProps> = () => {
    
    // const { formProps, saveButtonProps } = useForm<IPermissionDocument>();
    
    const { formProps, saveButtonProps, queryResult } = useForm<IPermissionDocument>();

    const postData = queryResult?.data?.data;

    return (
        <Edit saveButtonProps={{ ...saveButtonProps }}>
            <Form {...formProps} layout="vertical">
                <Form.Item
                    label="Permission Document"
                    name="permission_document"                    
                    rules={[
                        {
                            required: true,
                        },
                    ]}
                >
                          {/* <pre>
        <label>Enter value : </label> */}
        <MDEditor   preview='edit' data-color-mode="light"     value={JSON.stringify(queryResult?.data?.data.permission_document, null, 2)}>                                         </MDEditor>
        {/* <Input type="textarea" 
          name="textValue" defaultValue={postData ? JSON.stringify(postData?.permission_document, null, 2) : "Loading..."}
        /> */}
      {/* </pre> */}
                    
                {/* <MDEditor 
                    id="permission_document" 
                    preview='edit' data-color-mode="light"                
                /> */}
                </Form.Item>
            </Form>
        </Edit>
    );
};
