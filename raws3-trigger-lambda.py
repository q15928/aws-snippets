import boto3
import urllib
import json
import os

print("loading function")

s3 = boto3.client("s3")
glue = boto3.client("glue")

def lambda_handler(event, context):
    print("event: ", event)
    source_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    target_bucket = os.getenv("target_bucket")
    copy_source = {
        "Bucket": source_bucket,
        "Key": key
    }

    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(**copy_source)
        print(f"copying object {key} from source bucket {source_bucket} to target bucket {target_bucket}")
        s3.copy_object(Bucket=target_bucket, Key=key, CopySource=copy_source)
    except Exception as e:
        print(e)
        raise e