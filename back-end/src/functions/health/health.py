import os
import json
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())

def lambda_handler(event, context):
    
    LOGGER.info('Event structure: %s', event)
    LOGGER.info('Context structure: %s', context)    
    
    headers = event.get('headers')
    
    if headers:
        source_region = headers.get('Source-Region')
        destination_region = headers.get('Destination-Region')
        source_platform = headers.get('Source-Platform')
    else:
        source_region = 'null'
        destination_region = 'null'
        source_platform = 'null'

    json_data = {
        "environment": {
            'env': os.environ['Env'],
            'region': os.environ['Region'],
            'region_alias': os.environ['RegionAlias'],
            'component': os.environ['Component'],
            'project': os.environ['Project']
        }
    }        
    
    return {
        'statusCode': 200,
        'body': json.dumps(json_data),
        'headers': {        
            'Source-Region': source_region,
            'Destination-Region': destination_region,
            'Source-Platform': source_platform
        }
    }
    