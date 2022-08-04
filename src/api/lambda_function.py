import json, boto3, os

dynamodb = boto3.client("dynamodb")


def lambda_handler(event, context):
    print(f"event: {json.dumps(event)}")

    codes = event["queryStringParameters"]["codes"].split(",")
    results = []

    for x in codes:
        for y in codes:
            # our table does not have any records where the partition-key x is equal to the sort-key y, so we skip x == y scenarios
            if x == y:
                continue
            else:
                # sends a get-request to dynamodb for partition-key x and sort-key y
                response = dynamodb.get_item(
                    TableName=os.environ["dynamodb_table"],
                    Key={
                        "code1": {"S": x},
                        "code2": {"S": y},
                    },
                )

                # if dynamodb has a record for these keys, then it returns an "Item" and we store it in our results variable
                if "Item" in response:
                    code1 = response["Item"]["code1"]["S"]
                    code2 = response["Item"]["code2"]["S"]
                    error_code = response["Item"]["error_code"]["N"]

                    results.append((code1, code2, error_code))
    print(results)

    return {"statusCode": 200, "body": json.dumps({"results": results})}
