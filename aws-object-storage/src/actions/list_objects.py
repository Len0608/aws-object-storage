"""List Objects action — lists all objects in an S3 bucket."""

import logging
import os

from actions.output import ActionOutput
from exceptions import ValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import S3ClientFactory, S3Operations

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()

_DEFAULT_MAX_RECORDS: int = 100
_MAX_RECORDS_ENV_VAR: str = "UE_MAX_OUTPUT_RECORDS"


def list_objects(input_data: InputFields) -> ActionOutput:
    """List all objects in the specified S3 bucket.

    Paginates through all bucket objects via the S3 list_objects_v2 API,
    applies an output cap from UE_MAX_OUTPUT_RECORDS, and returns an
    ActionOutput whose print_output() renders an ASCII table and whose
    to_dict() builds the Extension Output JSON result object.

    Args:
        input_data: Validated input fields from the UAC task form.

    Returns:
        ActionOutput containing the paginated object list, counts, and
        bucket name for STDOUT rendering and Extension Output JSON.

    Raises:
        ValidationError:      When a required input field is missing or empty.
        AuthenticationError:  When AWS credentials are invalid or insufficient.
        BucketNotFoundError:  When the target bucket does not exist or is
                              inaccessible in the configured region.
        S3OperationError:     When a network or unexpected S3 service error
                              occurs during paginated listing.
    """
    logger.info("Starting list_objects action")
    logger.debug(
        "Input: action=%s, aws_region=%s, bucket_name=%s",
        input_data.action.value if input_data.action else None,
        input_data.aws_region.value if input_data.aws_region else None,
        input_data.bucket_name.value if input_data.bucket_name else None,
    )

    # Step 1: Input Validation
    if input_data.aws_credentials is None:
        raise ValidationError("aws_credentials is required")
    if not input_data.aws_region or input_data.aws_region.value == "":
        raise ValidationError("aws_region is required and must not be empty")
    if not input_data.bucket_name or input_data.bucket_name.value == "":
        raise ValidationError("bucket_name is required and must not be empty")

    bucket_name: str = input_data.bucket_name.value
    aws_region: str = input_data.aws_region.value
    access_key_id: str = input_data.aws_credentials.user
    secret_access_key: str = input_data.aws_credentials.password

    # Step 2: Read Output Cap
    max_records: int = _DEFAULT_MAX_RECORDS
    env_val = os.environ.get(_MAX_RECORDS_ENV_VAR)
    if env_val is not None:
        try:
            parsed = int(env_val)
            if parsed > 0:
                max_records = parsed
        except ValueError:
            logger.warning(
                "Invalid value for %s='%s'; using default %d",
                _MAX_RECORDS_ENV_VAR,
                env_val,
                _DEFAULT_MAX_RECORDS,
            )
    logger.debug("Output cap: %d records (env=%s)", max_records, env_val)

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
        # Step 4: Paginate and Collect All Objects
        s3_ops = S3Operations(client)
        objects, total_count = s3_ops.list_objects(bucket_name)

        # Step 5: Apply Output Cap
        displayed_count: int = min(total_count, max_records)
        capped_objects = objects[:displayed_count]
        logger.info(
            "Listing complete: total=%d displayed=%d",
            total_count,
            displayed_count,
        )

        # Step 7: Set Output Field
        output_data.update(object_count=str(total_count))
        logger.debug("Set object_count output field: %d", total_count)

    finally:
        # Step 9: Cleanup — always close HTTP session
        factory.close()

    logger.info(
        "list_objects action completed: listed %d objects in bucket '%s'",
        total_count,
        bucket_name,
    )

    # Step 8: Return Result
    return ActionOutput(
        bucket=bucket_name,
        total_count=total_count,
        displayed_count=displayed_count,
        objects=capped_objects,
    )
