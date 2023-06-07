import os
import json
import logging
import requests 

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    region = os.environ['Region']
    base_url = os.environ['BaseUrl']

    if 'queryStringParameters' in event:
        address =  event['queryStringParameters'].get('address')

    if address == None or address == "undefined":
        return {
            'statusCode': 502,
            'body': json.dumps({
                "message": "Bad Request - No address provided",
                "reason": "Please provide the address",
            }),
        } 
        
    # Get the auth flow from the body
    if event.get('body'):
        auth_flow = json.loads(event['body'])
    else:
        auth_flow = event['auth_flow']
    
    # First clean the data
    cleaned_allow_action_edges = []
    cleaned_deny_action_edges = []
    edges = auth_flow.get('edges')
    for edge in edges:
        print(edge)
        if edge.get('target') == "allow_effect":
            allow_action_source = edge.get('source')
            print("The following action source is connected to the allow effect:", allow_action_source)
            # check if allow_action_source is also connected to user
            for edge2 in edges:
                if edge2.get('source') == 'user' and edge2.get('target') == allow_action_source:
                    print("The following allow_action_source is also connected to the user:", allow_action_source)
                    print("Add to cleaned_allow_action_edges")
                    allow_action_source = allow_action_source.replace('_action', '')
                    cleaned_allow_action_edges.append(allow_action_source)
  
        if edge.get('target') == "deny_effect":
            deny_action_source = edge.get('source')
            print("The following action source is connected to the deny effect:", deny_action_source)
            # check if deny_action_source is also connected to user
            for edge2 in edges:
                if edge2.get('source') == 'user' and edge2.get('target') == deny_action_source:
                    print("The following deny_action_source is also connected to the user:", deny_action_source)
                    print("Add to cleaned_deny_action_edges")
                    deny_action_source = deny_action_source.replace('_action', '')
                    cleaned_deny_action_edges.append(deny_action_source)      
        
    print(cleaned_allow_action_edges)    
    print(cleaned_deny_action_edges)    

    allow_permission_document = {
        "address": address,
        "status": "draft",
        "chain": "sepolia",
        "signature": "unsigned",
        "version": "unknown",
        "permission_document": { 
            "Version": "2023-05-11",
            "Statement": [
                {
                    "Resource": [
                        "*"
                    ],
                    "Effect": "Allow",
                    "Action": cleaned_allow_action_edges,
                    "Principal": [
                        "*"
                    ],
                    "Sid": "AllowPermissions"
                }
            ],
            "Signature": "unsigned"
        }
    }

    deny_permission_document = {
        "address": address,
        "status": "draft",
        "chain": "sepolia",
        "signature": "unsigned",
        "version": "unknown",
        "permission_document": { 
            "Version": "2023-05-11",
            "Statement": [
                {
                    "Resource": [
                        "*"
                    ],
                    "Effect": "Deny",
                    "Action": cleaned_deny_action_edges,
                    "Principal": [
                        "*"
                    ],
                    "Sid": "DenyPermissions"
                }
            ],
            "Signature": "unsigned"
        }
    }
    
    
    combined_permission_document = {
        "address": address,
        "status": "draft",
        "chain": "sepolia",
        "signature": "unsigned",
        "version": "unknown",
        "permission_document": { 
            "Version": "2023-05-11",
            "Statement": [
                {
                    "Resource": [
                        "*"
                    ],
                    "Effect": "Allow",
                    "Action": cleaned_allow_action_edges,
                    "Principal": [
                        "*"
                    ],
                    "Sid": "AllowPermissions"
                },
                {
                    "Resource": [
                        "*"
                    ],
                    "Effect": "Deny",
                    "Action": cleaned_deny_action_edges,
                    "Principal": [
                        "*"
                    ],
                    "Sid": "DenyPermissions"
                }
            ],
            "Signature": "unsigned"
        }
    }
    
    if cleaned_allow_action_edges == [] and cleaned_deny_action_edges == []:
        LOGGER.info("No actions configured")
        return {
            'statusCode': 404,
            'body': json.dumps({"message": "No actions configured"}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    if cleaned_allow_action_edges == [] and cleaned_deny_action_edges != []:
        permission_document = deny_permission_document
    elif cleaned_allow_action_edges != [] and cleaned_deny_action_edges == []:
        permission_document = allow_permission_document
    else:
        permission_document = combined_permission_document
        
    print(permission_document)
    # Create the permission document 
    LOGGER.info('Creating the permission document')
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        created_permission_document_response = requests.post(base_url + '/public/ANY/v0/permission-documents', json = permission_document , headers=headers)
        if created_permission_document_response.status_code != 200:
            raise Exception("Error creating the permission document", permission_document, created_permission_document_response.json())   
    except Exception as err:
        LOGGER.error(err)
    
    created_permission_document_result = created_permission_document_response.json()
    id = created_permission_document_result.get('id')

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success", 'id': id}),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }


