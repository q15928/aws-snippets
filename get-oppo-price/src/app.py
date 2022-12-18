import json
import re
import os
import requests
import boto3

client = boto3.client('sns')

def lambda_handler(event, context):
    url = 'https://www.harveynorman.com.au/oppo-a96-128gb-starry-black.html'

    session = requests.session()
    headers = {
        "referer":"referer: https://www.google.com/",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    }
    session.post(url, headers=headers)
    response = session.get(url, headers=headers)
    resp_html = response.content.decode()
    m = re.search(r'displayPrice.*?(\d+)";', resp_html)
    if m:
        price = int(m.groups()[0])
        note = f'Oppo A96 price at Harvey Norman is {price}'
        sns_resp = client.publish(
            TargetArn = os.environ['SNStopic'], 
            Message = json.dumps({'default': note}),
            MessageStructure = 'json'
        )
        return {
            'statusCode': 200,
            'body': json.dumps(sns_resp)
        }
    else:
        print("Can't find the price at Harvey Norman")
