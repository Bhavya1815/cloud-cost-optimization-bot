import boto3

from .config import (
    AWS_ENDPOINT_URL,
    AWS_PROFILE,
    AWS_REGION,
)


def get_session():
    session_kwargs = {
        "region_name": AWS_REGION,
    }

    if AWS_PROFILE:
        session_kwargs["profile_name"] = AWS_PROFILE

    return boto3.Session(
        **session_kwargs,
    )


def get_ec2_client():
    session = get_session()

    client_kwargs = {
        "region_name": AWS_REGION,
    }

    if AWS_ENDPOINT_URL:
        client_kwargs["endpoint_url"] = AWS_ENDPOINT_URL

    return session.client(
        "ec2",
        **client_kwargs,
    )
