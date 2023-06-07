export interface ICategory {
    id: string;
    title: string;
}

export interface ITags {
    id: string;
    title: string;
}

export interface IPost {
    id: string;
    title: string;
    content: string;
    status: "published" | "draft" | "rejected";
    category: ICategory;
    tags: ITags[];
}

export interface IDispute {
    id: string;
    transaction_hash: string;
    created_by: string;
    resource_address: string;
    chain: string;
    action: string
    function_abi: string;
    contract_abi: string;
    status: "published" | "draft" | "rejected";
    result_hash: string;
    proof_hash_result: string;
    transaction_encoded_input_data: string;
    encoded_input_data: string
    decoded_input_data: string;
    notes: string;
    permission_document: IPermissionDocument;
    linked_approval: string;
}

export interface IPost2 {
    id: string;
}

export interface IEvent {
    created_at: number;
    address: string;
    org: string;
    chain: string;
    criticality_level: string;
    message_summary: string;
    resource: string;
    message: string;
    link_id: string;
}

export interface IPermissionDocument {
    id: string;
    address: string;
    status: string;
    version: string;
    version_ref: string;
    signature: string;
    permission_document: IPermissionDocumentStatement;
}

export interface IPermissionDocumentStatement {
    id: string;
    Version: string
    Statement: array[];
    Signature: string;
}


export interface ITransaction {
    hash: string;
    nonce: string;
    chain: string;
    transaction: object;
    address: string;
    from_address: string;
    to_address: string;
    value: string;
    gas: string;
    gas_price: string;
    input: string;
    receipt_cumulative_gas_used: string;
    receipt_gas_used: string;
    receipt_contract_address: string;
    receipt_root: string;
    receipt_status: string;
    block_timestamp: string;
    block_number: string;
    block_hash: string;
    transfer_index: array[]; 
    resource_address: string;
    status: string; // Custom added
    encoded_data: string; // Custom added
    transaction_encoded_input_data: string; // Custom added
    decoded_input_data: string; // Custom added
    decoded_input_function: string // Custom added
    is_confirmed: bool; // Custom added
    permission_documents_sender: IPermissionDocumentStatement; // Custom added
    error_reason: string; // Custom added
    encode_message_hash: string; // Custom added
    verified_encode_message_hash: string; // Custom added
}