This lab provides a static website which the user can post a text as the input. It will convert to speech and user can play back.

 will trigger lambda functions to create a new record in the backend DynamoDB as well as send a notification via SNS to trigger another lambda function which
arn:aws:sns:us-west-2:718758143626:new_posts

lambda execution policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "polly:SynthesizeSpeech",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "sns:Publish",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "*"
            ],
            "Effect": "Allow"
        }
    ]
}

S3 bucket public access policy
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::www-audioposts-20190626/*"
            ]
        }
    ]
}


endpoint:
http://www-audioposts-20190626.s3-website-us-west-2.amazonaws.com