from datetime import datetime, timezone

from .dynamodb_store import get_dynamodb_resource


TABLE_NAME = "cost-optimization-approvals"


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
                    "AttributeName": "approval_id",
                    "KeyType": "HASH",
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "approval_id",
                    "AttributeType": "S",
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.wait_until_exists()

    return dynamodb.Table(TABLE_NAME)


def save_approval_request(approval):
    """Save a new approval request to DynamoDB."""

    table = create_table_if_not_exists()

    table.put_item(
        Item=approval
    )

    return approval


def get_approval_request(approval_id):
    """Retrieve an approval request by ID."""

    table = create_table_if_not_exists()

    response = table.get_item(
        Key={
            "approval_id": approval_id
        }
    )

    return response.get("Item")


def update_approval_status(
    approval_id,
    status
):
    """Update the status of an approval request."""

    table = create_table_if_not_exists()

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    table.update_item(
        Key={
            "approval_id": approval_id
        },
        UpdateExpression=(
            "SET #status = :status, "
            "updated_at = :updated_at"
        ),
        ExpressionAttributeNames={
            "#status": "status"
        },
        ExpressionAttributeValues={
            ":status": status,
            ":updated_at": timestamp,
        },
    )

    return get_approval_request(
        approval_id
    )
