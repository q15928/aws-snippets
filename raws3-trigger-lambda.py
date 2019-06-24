"""
Lambda function to detect a new upload on S3 bucket, then trigger glue to
build data catalog with crawler

Required env variables:
DB_NAME
"""

import boto3
import urllib
import json
import os

print("loading function")

s3 = boto3.client("s3")
glue = boto3.client("glue")

def lambda_handler(event, context):
    # print("event: ", event)
    source_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    source_property = {
        "Bucket": source_bucket,
        "Key": key
    }
    folder_path = os.path.dirname("s3://" + source_bucket + "/" + key)
    
    # if a folder is created, just return
    if key.endswith("/"):
        return

    db_name = os.getenv("DB_NAME")
    crawler_name = os.path.splitext(os.path.basename(key))[0]
    db_params, cl_params = {}, {}
    db_params["Name"] = db_name
    db_params["Description"] = "Testing data catalog with lambda"
    cl_params["Name"] = crawler_name
    cl_params["Role"] = "service-role/AWSGlueServiceRole-crawlerTest"
    cl_params["DatabaseName"] = db_name
    cl_params["Targets"] = {}
    cl_params["Targets"]["S3Targets"] = [{"Path": folder_path}]

    try:
        waiter = s3.get_waiter("object_exists")
        waiter.wait(**source_property)

        # create a database in the data catalog if not exists
        try:
            exist_db = glue.get_database(Name=db_name)
            print(exist_db)
            glue.update_database(Name=db_name, DatabaseInput=db_params)
        except:
            db_resp = glue.create_database(DatabaseInput=db_params)
            print(f"Database {db_name} created, details: {db_resp}")

        # create a crawler if not exists
        try:
            exist_cl = glue.get_crawler(Name=cl_params["Name"])
            print(exist_cl)
            glue.update_crawler(**cl_params)
        except:
            cl_resp = glue.create_crawler(**cl_params)
            print(f"Crawler {cl_params['Name']} created, details: {cl_resp}")

        # start the crawler
        print(f"Start crawler on {cl_params['Targets']['S3Targets']}")
        glue.start_crawler(Name=crawler_name)
    except Exception as e:
        print(e)
        raise e