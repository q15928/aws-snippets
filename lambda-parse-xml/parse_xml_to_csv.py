import csv
from datetime import datetime
import os
from urllib.parse import unquote_plus
import xml.etree.ElementTree as ET

import boto3

s3_client = boto3.client('s3')

# columns for the DataFrame
COL_NAMES = ['book_id', 'author', 'title', 'genre', 'price', 'publish_date',
            'description']
ELEMENTS_TO_EXTRAT = [c for c in COL_NAMES if c != 'book_id']


def parse_xml(xml_content, upload_path):
    """
    Read the xml string, parse and extract the elements,
    then write to a csv file.
    """
    results = []
    root = ET.fromstring(xml_content)

    for b in root.findall('book'):
        rec = []
        rec.append(b.attrib['id'])
        for e in ELEMENTS_TO_EXTRAT:
            if b.find(e) is None:
                rec.append(None)
                continue
            value = b.find(e).text
            if e == 'price':
                value = float(value)
            elif e == 'publish_date':
                value = datetime.strptime(value, '%Y-%m-%d')
            rec.append(value)
        results.append(rec)

    with open(upload_path, 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(COL_NAMES)
        csvwriter.writerows(results)


def lambda_handler(event, context):
    for rec in event['Records']:
        bucket = rec['s3']['bucket']['name']
        key = unquote_plus(rec['s3']['object']['key'])
        print("{}/{} is uploaded to S3".format(bucket, key))

        # no need to parse if a folder is created
        if key.endswith('/'):
            return

        processed_file = os.path.splitext(os.path.basename(key))[0] + '.csv'
        processed_key = os.path.join('csv', processed_file) 
        upload_path = '/tmp/processed-{}'.format(processed_file)
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        xml_content = obj['Body'].read()
        parse_xml(xml_content, upload_path)
        s3_client.upload_file(upload_path, bucket, processed_key)
