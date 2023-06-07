import os
import json
import logging
from typing import Any

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    # LOGGER.info(event)

    if event.get('body'):
        body = event["body"]
    else:
        body = event["permission_document"]

    # LOGGER.info(body)
    permission_document = json.loads(body)

    # LOGGER.info(permission_document)

    # Validate the model of the permission documents
    try:
        validated_permission_document = validate_model(permission_document) # raises error
    except Exception as err:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0]
            }),
        }
    
    # Validate the attributes of the statements
    statements = validated_permission_document.Statement
    try:
        find_duplicate_sids(statements) # raises error
    except Exception as err:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        }

    # Validate the version
    version = validated_permission_document.Version
    try:
        validate_version(version) # raises error
    except Exception as err:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        } 

    try:
        validate_attributes(statements) # raises error
    except Exception as err:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "message": "error",
                "reason": err.args[0],
                "detailed_reason": err.args[1:]
            }),
        }  

    # If all ok then return 200
    return {
        'statusCode': 200,
        'body': json.dumps({"message": "success"}),
    }




def find_duplicate_sids(statements):
    # find duplicate Sid's
    unique_statements_list = []
    duplist = []
    for obj in statements:
        if(obj.Sid in unique_statements_list):
            duplist.append(obj.Sid)
        else:
            unique_statements_list.append(obj.Sid)  
    
    if len(duplist) > 0:
        raise Exception("Duplicate Sids found in the permission document:", *duplist)

def validate_model(permission_document):
    # Validate if it follows the permisison document model

    # json_permission_document = '''{"Version":"2023-05-11", "Signature": "dwfwefwef", "Statement":[{"Sid":"TestPermissions", "Effect":"Allow", "Action": "transfer", "Principal": "*", "Resource": "*"}, {"Sid":"TestPermissions", "Effect":"Allow", "Action": "trans2fer", "Principal": "*", "Resource": "*"}]}'''

    # dict_permission_document = json.loads(json_permission_document)
    # u = PermissionDocument(**json_permission_document)
    # for statement in u.Statement:
    #     print(statement)

    validated_permission_document = PermissionDocument(**permission_document)
    LOGGER.info(validated_permission_document)

    return validated_permission_document

def validate_version(version):
    allowed_version_values = ['2023-05-11']

    if version not in allowed_version_values:
        raise Exception("Version contains incorrect 'Version'", version, "Allowed values are:", *allowed_version_values)   

    return True

def validate_attributes(statements):
    # Validate the attributes and if it follow the permisison document model
    for statement in statements:
        effect = statement.Effect
        allowed_effect_values = ['Allow', 'Deny']
        if effect not in allowed_effect_values:
            raise Exception("Statement contains incorrect 'Effect'", statement.__dict__, "Allowed values are:", *allowed_effect_values)

        actions = statement.Action
        allowed_action_values_0 = ['*', 'ERC20']
        allowed_action_values_1 = ['*', 'AUTHE', 'LINK', 'ETH', 'USDC']
        allowed_action_values_2 = ['*', 'transfer', 'approve', 'transferFrom', 'allowance', 'mint']
        for action in actions:
            if action == "*":
                continue 
            if len(action.split(':')) == 1:
                if action.split(':')[0] not in allowed_action_values_2:
                    raise Exception("Statement contains incorrect 'Action'", statement.__dict__, "Allowed values are:", *allowed_action_values_2)  
                continue
            if len(action.split(':')) != 3:
                raise Exception("Statement contains incorrect 'Action'", statement.__dict__)   

            if action.split(':')[0] not in allowed_action_values_0:
                raise Exception("Statement contains incorrect 'Action'", statement.__dict__, "Allowed values are:", *allowed_action_values_0)     

            if action.split(':')[1] not in allowed_action_values_1:
                raise Exception("Statement contains incorrect 'Action'", statement.__dict__, "Allowed values are:", *allowed_action_values_1)   

            if action.split(':')[-1] not in allowed_action_values_2:
                raise Exception("Statement contains incorrect 'Action'", statement.__dict__, "Allowed values are:", *allowed_action_values_2)     

        principals = statement.Principal
        allowed_principal_values = ['*', '0x1234567890123456789012345678901234567890']
        # Should be valid address
        for principal in principals:
            if principal not in allowed_principal_values:
                raise Exception("Statement contains incorrect 'Principal'", statement.__dict__, "Should be a valid address or wildcard '*'")     

        resources = statement.Resource
        allowed_resource_values = ['*', '0x1234567890123456789012345678901234567890']
        for resource in resources:
            # Should be valid address or '*'
            if resource not in allowed_resource_values:
                raise Exception("Statement contains incorrect 'Resource'", statement.__dict__, "Should be a valid address or wildcard '*'")     

    return True


class StatementClass(object):
    def __init__(self, Sid, Effect, Action, Principal, Resource):
        self.Sid = Sid
        self.Effect = Effect
        self.Action = Action
        self.Principal = Principal
        self.Resource = Resource

    def __str__(self):
        return "{0} {1} {2}".format(self.Sid, self.Effect, self.Action, self.Principal, self.Resource)
    
    def from_dict(Sid, Effect, Action, Principal, Resource) -> 'Statement':
        _Sid = str(Sid)
        _Effect = str(Effect)
        _Action = list(Action)
        _Principal = list(Principal)
        _Resource = list(Resource)
        return StatementClass(_Sid, _Effect, _Action, _Principal, _Resource)

class PermissionDocument(object):
    def __init__(self, Version, Signature, Statement):
        self.Version = Version
        self.Signature = Signature
        self.Statement = list(StatementClass.from_dict(**y) for y in Statement)

    def __str__(self):
        return "{0} ,{1}".format(self.Version, self.Signature, self.Statement)

    def from_dict(obj: Any) -> 'PermissionDocument':
        _Version = str(obj.get("Version"))
        _Signature = str(obj.get("Signature"))
        _Statement = [StatementClass.from_dict(**y) for y in obj.get("Statement")]
        return Root(_Version, _Statement)

