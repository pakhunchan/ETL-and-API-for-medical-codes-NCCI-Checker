import json, boto3, os

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    print(f"event: {json.dumps(event)}")

    sqs_message = json.loads(event["Records"][0]["body"])

    # polls for message from SQS queue. Return bucket name, object name, starting row, and ending row.
    bucket = sqs_message["Bucket"]
    key = sqs_message["Key"]
    start = sqs_message["start"]
    end = sqs_message["end"]

    # grab data from s3
    raw_data = s3.get_object(Bucket=bucket, Key=key)
    results = raw_data["Body"].read().decode("utf-8").split("\n")

    for i in range(start, end):
        code1, code2, error_code = results[i].split(",")
        code1 = code1.strip()
        code2 = code2.strip()
        error_code = error_code.strip()

        # error_code has 3 possible values: 0, 1, 9. An error_code value of 9 means that the record/policy has been deleted, so we should skip these records.
        if error_code == "9":
            continue

        # enter data into dynamodb
        dynamodb.put_item(
            TableName=os.environ["dynamodb_table"],
            Item={
                "code1": {"S": code1},
                "code2": {"S": code2},
                "error_code": {"N": error_code},
            },
        )

        print(f"row: {i}, code1: {code1}, code2: {code2}, error_code: {error_code}")
    print("Completed!")
