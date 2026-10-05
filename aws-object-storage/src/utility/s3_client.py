"""
S3ClientFactory — constructs and manages the lifecycle of the boto3 S3 client.

Centralises client creation so credentials are applied consistently across all
actions, and provides an explicit close method so the underlying HTTP session
is released in the action's finally block.
"""
import logging
from typing import Any

import boto3

logger = logging.getLogger("UNV")


class S3ClientFactory:
    """
    Constructs and manages the lifecycle of a boto3 S3 client.

    Usage pattern expected by callers::

        factory = S3ClientFactory(access_key_id, secret_access_key, region)
        client = factory.create_client()
        try:
            ...
        finally:
            factory.close()
    """

    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region_name: str,
    ) -> None:
        """
        Initialise the factory with AWS credentials and target region.

        Args:
            access_key_id:     AWS Access Key ID.
            secret_access_key: AWS Secret Access Key.
            region_name:       AWS region identifier (e.g. ``us-east-1``).
        """
        self._access_key_id: str = access_key_id
        self._secret_access_key: str = secret_access_key
        self._region_name: str = region_name
        self._client: Any = None

    def create_client(self) -> Any:
        """
        Construct and return a configured boto3 S3 client.

        The client is stored internally so it can be closed via :meth:`close`.

        Returns:
            A boto3 S3 client configured with the provided credentials and region.
        """
        logger.info("Creating S3 client for region: %s", self._region_name)
        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
            region_name=self._region_name,
        )
        logger.debug("S3 client created successfully")
        return self._client

    def close(self) -> None:
        """
        Close the client's underlying HTTP session to release connections.

        Safe to call even if :meth:`create_client` was never called or if the
        client is already closed.
        """
        if self._client is not None:
            logger.debug("Closing S3 client HTTP session")
            self._client.close()
            self._client = None
