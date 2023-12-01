import json

import boto3

from shared.sync import UpdateS3
from shared.config.env import NFL_DATA_BUCKET


def lambda_handler(event, context):
    method = event.get('method')

    s3 = boto3.client("s3")
    upater = UpdateS3(s3,  NFL_DATA_BUCKET)


    if method == "init_s3":
        print("initializing s3")
        upater.initialize_s3()
    else:
        print("updating s3")
        upater.update_s3()

    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "AWS Lambda Update NFL S3 Bucket function executed successfully",
            }
        ),
    }

    return response
