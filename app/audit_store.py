from .audit import build_audit_event
from .dynamodb_store import get_dynamodb_resource


TABLE_NAME = "cost-optimization-audit"


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
                    "AttributeName": "event_id",
                    "KeyType": "HASH",
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "event_id",
                    "AttributeType": "S",
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        table.wait_until_exists()

    return dynamodb.Table(TABLE_NAME)


def record_audit_event(
    event_type,
    *,
    instance_id=None,
    name=None,
    approval_id=None,
    status=None,
    message=None,
    metadata=None,
):
    event = build_audit_event(
        event_type,
        instance_id=instance_id,
        name=name,
        approval_id=approval_id,
        status=status,
        message=message,
        metadata=metadata,
    )

    table = create_table_if_not_exists()

    table.put_item(
        Item=event
    )

    return event


def safe_record_audit_event(
    logger,
    event_type,
    *,
    instance_id=None,
    name=None,
    approval_id=None,
    status=None,
    message=None,
    metadata=None,
):
    try:
        event = record_audit_event(
            event_type,
            instance_id=instance_id,
            name=name,
            approval_id=approval_id,
            status=status,
            message=message,
            metadata=metadata,
        )

        logger.info(
            "Audit event recorded: %s",
            event_type,
        )

        return event

    except Exception:
        logger.exception(
            "Failed to record audit event: %s",
            event_type,
        )

        return None


def list_audit_events(limit=100):
    table = create_table_if_not_exists()

    events = []

    scan_kwargs = {
        "Limit": 100,
    }

    while len(events) < limit:
        response = table.scan(
            **scan_kwargs
        )

        events.extend(
            response.get("Items", [])
        )

        last_evaluated_key = response.get(
            "LastEvaluatedKey"
        )

        if not last_evaluated_key:
            break

        scan_kwargs["ExclusiveStartKey"] = (
            last_evaluated_key
        )

        scan_kwargs.pop("Limit", None)

    events.sort(
        key=lambda event: event.get(
            "timestamp",
            "",
        ),
        reverse=True,
    )

    return events[:limit]
