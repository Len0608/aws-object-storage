"""Upload File action — uploads a local file to an S3 bucket."""

import logging
import os

from actions.output import ActionOutput
from exceptions import LocalFileNotFoundError, ValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import S3ClientFactory, S3Operations

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def upload_file(input_data: InputFields) -> ActionOutput:
    """Upload a local file from the agent host filesystem to S3.

    Validates all required inputs, verifies the local file exists, uploads
    the file to the specified S3 bucket and object key, and returns an
    ActionOutput whose print_output() renders the upload confirmation and
    whose to_dict() builds the Extension Output JSON result object.

    Args:
        input_data: Validated input fields from the UAC task form.

    Returns:
        ActionOutput containing the S3 URI, file size, bucket, key, and
        local file path for STDOUT rendering and Extension Output JSON.

    Raises:
        ValidationError:        When a required input field is missing or empty.
        LocalFileNotFoundError: When the local file does not exist on the
                                agent host filesystem.
        AuthenticationError:    When AWS credentials are invalid or insufficient.
        BucketNotFoundError:    When the target bucket does not exist or is
                                inaccessible in the configured region.
        S3OperationError:       When a network or unexpected S3 service error
                                occurs during the upload.
    """
    logger.info("Starting upload_file action")
    logger.debug(
        "Input: action=%s, aws_region=%s, bucket_name=%s, local_file=%s, s3_object_key=%s",
        input_data.action.value if input_data.action else None,
        input_data.aws_region.value if input_data.aws_region else None,
        input_data.bucket_name.value if input_data.bucket_name else None,
        input_data.local_file.value if input_data.local_file else None,
        input_data.s3_object_key.value if input_data.s3_object_key else None,
    )

    # Step 1: Input Validation
    if input_data.aws_credentials is None:
        raise ValidationError("aws_credentials is required")
    if not input_data.aws_region or input_data.aws_region.value == "":
        raise ValidationError("aws_region is required and must not be empty")
    if not input_data.bucket_name or input_data.bucket_name.value == "":
        raise ValidationError("bucket_name is required and must not be empty")
    if not input_data.local_file or input_data.local_file.value == "":
        raise ValidationError("local_file is required for the Upload File action")
    if not input_data.s3_object_key or input_data.s3_object_key.value == "":
        raise ValidationError("s3_object_key is required for the Upload File action")

    bucket_name: str = input_data.bucket_name.value
    aws_region: str = input_data.aws_region.value
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password
    local_file: str = input_data.local_file.value
    s3_object_key: str = input_data.s3_object_key.value

    # Verify file exists on the agent host filesystem
    logger.info("Verifying local file exists: %s", local_file)
    if not os.path.isfile(local_file):
        logger.error("Local file not found: %s", local_file)
        raise LocalFileNotFoundError("Local file not found: %s" % local_file)

    # Step 2: Retrieve File Size
    file_size_bytes: int = os.path.getsize(local_file)
    logger.debug("Local file size: %d bytes", file_size_bytes)

    # Compose S3 URI (Step 5 — available before upload for logging)
    s3_uri: str = "s3://%s/%s" % (bucket_name, s3_object_key)
    logger.info("Target S3 URI: %s", s3_uri)

    # Initialise OutputFields for real-time UI updates
    output_data: OutputFields = OutputFields()

    # Step 3: Construct S3 Client
    logger.info("Constructing S3 client for region: %s", aws_region)
    factory = S3ClientFactory(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region_name=aws_region,
    )
    client = factory.create_client()

    try:
        # Step 4: Upload File to S3
        s3_ops = S3Operations(client)
        s3_ops.upload_file(
            local_file=local_file,
            bucket_name=bucket_name,
            s3_object_key=s3_object_key,
        )

        # Step 7: Set Output Field
        output_data.update(s3_uri=s3_uri)
        logger.debug("Set s3_uri output field: %s", s3_uri)

    finally:
        # Step 9: Cleanup — always close HTTP session
        factory.close()

    logger.info(
        "upload_file action completed: uploaded '%s' to %s",
        local_file,
        s3_uri,
    )

    # Step 8: Return Result
    return ActionOutput(
        bucket=bucket_name,
        key=s3_object_key,
        s3_uri=s3_uri,
        size_bytes=file_size_bytes,
        local_file=local_file,
    )
