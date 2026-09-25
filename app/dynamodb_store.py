from datetime import datetime, timezone

from .aws_client import get_session
from .config import (
    AWS_ENDPOINT_URL,
    AWS_REGION,
)


TABLE_NAME = "cost-optimization-recommendations"


def get_dynamodb_resource():
    session = get_session()

    resource_kwargs = {
        "region_name": AWS_REGION,
    }

    if AWS_ENDPOINT_URL:
        resource_kwargs["endpoint_url"] = (
            AWS_ENDPOINT_URL
        )

    return session.resource(
        "dynamodb",
        **resource_kwargs,
    )


def create_table_if_not_exists():
    dynamodb = get_dynamodb_resource()

    existing_tables = [
        table.name
        for table in dynamodb.tables.all()
    ]

    if TABLE_NAME not in existing_tables:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    "AttributeName": "instance_id",
                    "KeyType": "HASH",
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "instance_id",
                    "AttributeType": "S",
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.wait_until_exists()

    return dynamodb.Table(TABLE_NAME)


def save_recommendations(recommendations):
    table = create_table_if_not_exists()
    timestamp = datetime.now(timezone.utc).isoformat()

    new_recommendations = []

    for recommendation in recommendations:
        instance_id = recommendation["instance_id"]

        response = table.get_item(
            Key={
                "instance_id": instance_id
            }
        )

        existing_item = response.get("Item")

        if existing_item is None:
            status = "NEW"
            is_new = True

        elif existing_item.get("status") == "RESOLVED":
            status = "NEW"
            is_new = True

        else:
            status = "ACTIVE"
            is_new = False

        if is_new:
            item = {
                "instance_id": instance_id,
                "name": recommendation["name"],
                "instance_type": recommendation[
                    "instance_type"
                ],
                "action": recommendation["action"],
                "reason": recommendation["reason"],
                "cpu_utilization": str(
                    recommendation[
                        "cpu_utilization"
                    ]
                ),
                "estimated_monthly_cost": str(
                    recommendation[
                        "estimated_monthly_cost"
                    ]
                ),
                "estimated_monthly_savings": str(
                    recommendation[
                        "estimated_monthly_savings"
                    ]
                ),
                "created_at": timestamp,
                "updated_at": timestamp,
                "status": status,
            }

            table.put_item(Item=item)
            new_recommendations.append(
                recommendation
            )

        else:
            table.update_item(
                Key={
                    "instance_id": instance_id
                },
                UpdateExpression=(
                    "SET #status = :status, "
                    "updated_at = :updated_at, "
                    "cpu_utilization = :cpu, "
                    "reason = :reason"
                ),
                ExpressionAttributeNames={
                    "#status": "status",
                },
                ExpressionAttributeValues={
                    ":status": "ACTIVE",
                    ":updated_at": timestamp,
                    ":cpu": str(
                        recommendation[
                            "cpu_utilization"
                        ]
                    ),
                    ":reason": recommendation[
                        "reason"
                    ],
                },
            )

    return new_recommendations


def resolve_missing_recommendations(
    current_recommendations,
):
    table = create_table_if_not_exists()

    current_ids = {
        recommendation["instance_id"]
        for recommendation
        in current_recommendations
    }

    response = table.scan()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    resolved_count = 0

    for item in response.get("Items", []):
        instance_id = item["instance_id"]

        if instance_id not in current_ids:
            if item.get("status") in {
                "NEW",
                "ACTIVE",
            }:
                table.update_item(
                    Key={
                        "instance_id": instance_id
                    },
                    UpdateExpression=(
                        "SET #status = :status, "
                        "updated_at = :updated_at"
                    ),
                    ExpressionAttributeNames={
                        "#status": "status"
                    },
                    ExpressionAttributeValues={
                        ":status": "RESOLVED",
                        ":updated_at": timestamp,
                    },
                )

                resolved_count += 1

    return resolved_count
