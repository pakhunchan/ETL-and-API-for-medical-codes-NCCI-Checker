import json, boto3, os

s3 = boto3.client("s3")
sqs = boto3.client("sqs")


def lambda_handler(event, context):
    print(f"event = {json.dumps(event)}")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    raw_data = s3.get_object(Bucket=bucket, Key=key)
    results = raw_data["Body"].read().decode("utf-8").split("\n")

    total_rows = len(results)
    # want increments of 1000. +1 in the end to grab all the remainder in the last set of rows.
    number_of_splits = (total_rows // 1000) + 1
    start = 0
    end = 1000

    for _ in range(1, number_of_splits + 1):
        start += 1000
        end += 1000

        message = json.dumps(
            {
                "start": start,
                "end": end,
                "Bucket": bucket,
                "Key": key,
            }
        )

        sqs.send_message(QueueUrl=os.environ["queue_url"], MessageBody=message)
