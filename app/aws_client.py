import boto3

from .config import (
    AWS_ENDPOINT_URL,
    AWS_REGION,
)


def get_session():
    return boto3.Session(
        region_name=AWS_REGION,
    )


def get_ec2_client():
    session = get_session()

    return session.client(
        "ec2",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
    )
