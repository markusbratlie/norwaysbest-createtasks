import json

import main


def lambda_handler(event, context):
    dry_run = False
    if 'dry_run' in event:
        dry_run = event['dry_run']

    client = main.norwaysBestClient()

    client.main()

    return {
        'statusCode': 200,
        'body': "sucsess"
    }
