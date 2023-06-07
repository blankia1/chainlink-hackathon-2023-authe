import os
import json
import logging
import requests
from collections import OrderedDict

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    if event.get('body'):
        oracle_decoded_request = json.loads(event['body']).get('oracle_decoded_request')
        permission_documents = json.loads(event['body']).get('permission_documents')
    else:
        oracle_decoded_request = json.loads(event['oracle_decoded_request'])
        permission_documents = json.loads(event['permission_documents'])

    _from = oracle_decoded_request['f']
    to =  oracle_decoded_request['t']
    function_name =  oracle_decoded_request['n']
    decoded_data =  oracle_decoded_request['d']  
    resource =  oracle_decoded_request['r']

    LOGGER.info(oracle_decoded_request)
    LOGGER.info(permission_documents)
    LOGGER.info(_from)
    LOGGER.info(to)
    LOGGER.info(function_name)
    LOGGER.info(decoded_data)
    
    # Validate the permission documents belong to the oracle request
    if _from not in permission_documents:
        LOGGER.error("Error: from address is not in permission documents:" + _from)
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": "Address '" + _from + "' is not in matching the permission document"
            }),
        } 

    if resource not in permission_documents:
        LOGGER.error("Error: from resource is not in permission documents:" + resource)
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": "Address '" + resource + "' is not in matching the permission document"
            }),
        } 

    from_permission_statements = permission_documents[_from].get('Statement')
    resource_permission_statements = permission_documents[resource].get('Statement')

    # Check the permissions
    for statement in from_permission_statements:
        try:
            check_action_permissions(function_name, statement) # raises error
            check_principal_permissions(to, statement) # raises error
            check_resource_permissions(resource, statement) # raises error
        except Exception as err:
            LOGGER.error(err)
            # Return 403 when the permission document denies the action, principal or resource. All else throw 500 error
            if err.args[0] == "App 403 Forbidden":
                return {
                    'statusCode': 403,
                    'body': json.dumps({
                        "message": "forbidden",
                        "reason": err.args[0],
                        "detailed_reason": err.args[1:]
                    }),
                }  
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        "message": "error",
                        "reason": err.args[0]
                    }),
                } 

    # Check the permissions assigned on the resource level
    for statement in resource_permission_statements:
        try:
            check_action_permissions(function_name, statement) # raises error
            check_principal_permissions(to, statement) # raises error
            check_resource_permissions(resource, statement) # raises error
        except Exception as err:
            LOGGER.error(err)
            # Return 403 when the permission document denies the action, principal or resource. All else throw 500 error
            if err.args[0] == "App 403 Forbidden":
                return {
                    'statusCode': 403,
                    'body': json.dumps({
                        "message": "forbidden",
                        "reason": err.args[0],
                        "detailed_reason": err.args[1:]
                    }),
                }  
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        "message": "error",
                        "reason": err.args[0]
                    }),
                } 

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success"}),
    }
   
def check_action_permissions(_action, statement):
    actions = statement['Action']
    # Pytest unit test with policy without array
    if actions == _action:
        return True

    if "*" in actions:
        if statement['Effect'] == "Allow":
            return True
        else:
            # return False
            raise Exception("App 403 Forbidden", "Not allowed", statement, "action ->", _action)

    for action in actions:
        if (_action == action.split(':')[-1]):
            if statement['Effect'] == "Allow":
                return True
            else:
                # return False
                raise Exception("App 403 Forbidden", "Not allowed", statement, "action ->", _action)
        
        if statement['Effect'] == "Deny":
                return True
    raise Exception("App 403 Forbidden", "Not allowed", statement, "action ->", _action)
    

def check_principal_permissions(_principal, statement):
    principals = statement['Principal']
    print(*principals)
    # Pytest unit test with policy without array
    if principals == _principal:
        return True

    if "*" in principals:
        if statement['Effect'] == "Allow":
            return True
        else:
            # For now only explicit denies for principal
            return False
            # raise Exception("App 403 Forbidden", "Not allowed", statement, "action ->", _action)

    for principal in principals:
        if (_principal == principal):
            if statement['Effect'] == "Allow":
                return True
            else:
                # return False
                raise Exception("App 403 Forbidden", "Not allowed", statement, "_principal ->", _principal, "principals:", principals)

    raise Exception("App 403 Forbidden", "Not allowed", statement, "_principal ->", _principal, "principals:", principals)

def check_resource_permissions(_resource, statement):
    resources = statement['Resource']

    # Pytest unit test with policy without array
    if resources == _resource:
        return True

    if "*" in resources:
        if statement['Effect'] == "Allow":
            return True
        else:
            # For now only explicit denies for resources
            return False
            # raise Exception("App 403 Forbidden", "Not allowed", statement, "action ->", _action)

    for resource in resources:
        if (_resource == resource):
            if statement['Effect'] == "Allow":
                return True
            else:
                # return False
                raise Exception("App 403 Forbidden", "Not allowed", statement, "_resource ->", _resource)
    
    raise Exception("App 403 Forbidden", "Not allowed", statement, "_resource ->", _resource)
    