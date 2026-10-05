"""
S3Operations — encapsulates S3 API calls and maps botocore/boto3 ClientError
exceptions to domain-specific extension exceptions.

Error code mapping
------------------
Authentication errors (exit code 1, non-transient):
  InvalidClientTokenId, AuthFailure, AccessDenied, ExpiredToken,
  InvalidAccessKeyId -> AuthenticationError

Bucket access errors (exit code 1, user configuration):
  NoSuchBucket, NoSuchKey -> BucketNotFoundError

All other ClientError codes and network-level errors -> S3OperationError
"""
import logging
from datetime import timezone
from typing import Any, NoReturn

from botocore.exceptions import ClientError

from exceptions import (
    AuthenticationError,
    BucketNotFoundError,
    LocalFileNotFoundError,
    S3OperationError,
)

logger = logging.getLogger("UNV")

_AUTH_ERROR_CODES: frozenset[str] = frozenset(
    {
        "InvalidClientTokenId",
        "AuthFailure",
        "AccessDenied",
        "ExpiredToken",
        "InvalidAccessKeyId",
    }
)

_BUCKET_NOT_FOUND_CODES: frozenset[str] = frozenset({"NoSuchBucket", "NoSuchKey"})


class S3Operations:
    """
    Encapsulates S3 API calls for the two supported operations.

    All botocore ``ClientError`` exceptions are classified and re-raised as
    domain-specific extension exceptions so callers do not need to import
    botocore directly.
    """

    def __init__(self, client: Any) -> None:
        """
        Initialise with a pre-built boto3 S3 client.

        Args:
            client: A boto3 S3 client (as returned by :class:`S3ClientFactory`).
        """
        self._client: Any = client

    def _classify_client_error(self, error: ClientError) -> NoReturn:
        """
        Classify a ``ClientError`` by its AWS error code and raise the
        corresponding domain exception.

        Args:
            error: The botocore ``ClientError`` to classify.

        Raises:
            AuthenticationError:  For invalid/expired/insufficient credentials.
            BucketNotFoundError:  For missing or inaccessible buckets.
            S3OperationError:     For all other ClientError codes.
        """
        error_code: str = error.response.get("Error", {}).get("Code", "")
        logger.debug("Classifying ClientError code: %s", error_code)

        if error_code in _AUTH_ERROR_CODES:
            logger.error("AWS authentication error (code=%s): %s", error_code, str(error))
            raise AuthenticationError(str(error))

        if error_code in _BUCKET_NOT_FOUND_CODES:
            logger.error("Bucket not found (code=%s): %s", error_code, str(error))
            raise BucketNotFoundError(str(error))

        logger.error("S3 service error (code=%s): %s", error_code, str(error))
        raise S3OperationError(str(error))

    def list_objects(self, bucket_name: str) -> tuple[list[dict], int]:
        """
        Paginate through all objects in the bucket and return their metadata.

        Uses ``list_objects_v2`` with a paginator so buckets with more than
        1 000 objects are handled transparently.  All object metadata is
        accumulated before returning; the output cap is applied by the caller.

        Args:
            bucket_name: Name of the target S3 bucket.

        Returns:
            A tuple of ``(objects, total_count)`` where ``objects`` is a list
            of dicts with keys ``key`` (str), ``size`` (int), and
            ``last_modified`` (ISO 8601 UTC string), and ``total_count`` is the
            length of that list.

        Raises:
            AuthenticationError:  For invalid/expired credentials or insufficient
                                  IAM permissions.
            BucketNotFoundError:  When the bucket does not exist or is not
                                  reachable in the configured region.
            S3OperationError:     For network failures, throttling, or unexpected
                                  S3 service errors.
        """
        logger.info("Listing all objects in bucket: %s", bucket_name)
        objects: list[dict] = []

        try:
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket_name):
                for obj in page.get("Contents", []):
                    last_modified = obj["LastModified"]
                    if last_modified.tzinfo is not None:
                        last_modified_str = last_modified.astimezone(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%SZ"
                        )
                    else:
                        last_modified_str = last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")

                    objects.append(
                        {
                            "key": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": last_modified_str,
                        }
                    )
        except ClientError as exc:
            self._classify_client_error(exc)
        except Exception as exc:
            logger.error("Unexpected error while listing objects in bucket '%s': %s", bucket_name, str(exc))
            raise S3OperationError(str(exc))

        total_count: int = len(objects)
        logger.info("Retrieved %d objects from bucket: %s", total_count, bucket_name)
        return objects, total_count

    def upload_file(self, local_file: str, bucket_name: str, s3_object_key: str) -> None:
        """
        Upload a local file to the specified S3 bucket and object key.

        Args:
            local_file:    Absolute path to the file on the agent host.
            bucket_name:   Name of the target S3 bucket.
            s3_object_key: Destination key within the bucket.

        Raises:
            LocalFileNotFoundError: When the local file is not found (either
                                    before the call or as reported by boto3).
            AuthenticationError:    For invalid/expired credentials or insufficient
                                    IAM permissions.
            BucketNotFoundError:    When the bucket does not exist or is not
                                    reachable in the configured region.
            S3OperationError:       For network failures, throttling, or unexpected
                                    S3 service errors.
        """
        logger.info(
            "Uploading '%s' to s3://%s/%s",
            local_file,
            bucket_name,
            s3_object_key,
        )

        try:
            self._client.upload_file(
                Filename=local_file,
                Bucket=bucket_name,
                Key=s3_object_key,
            )
            logger.info(
                "File uploaded successfully to s3://%s/%s",
                bucket_name,
                s3_object_key,
            )
        except FileNotFoundError:
            logger.error("Local file not found during upload: %s", local_file)
            raise LocalFileNotFoundError("Local file not found: %s" % local_file)
        except ClientError as exc:
            self._classify_client_error(exc)
        except Exception as exc:
            logger.error("Unexpected error during upload of '%s': %s", local_file, str(exc))
            raise S3OperationError(str(exc))
