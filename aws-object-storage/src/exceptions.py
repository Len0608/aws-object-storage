"""
Exceptions module for the AWS Object Storage Universal Extension.

This module provides:
- Base ExecutionError class
- Standard exception types (DataValidationError, UnexpectedSystemError)
- AWS S3-specific exception hierarchy

Exit code conventions:
  0  - Success
  1  - Operational failure (authentication, resource, service, or network errors)
  20 - Input validation failure (missing or invalid required field values)
"""
from typing import Optional


class ExecutionError(Exception):
    """
    The default error raised by an extension.

    All extension errors must inherit from it.

    Attrs:
        exit_code: The exit code of the extension (for UAC)
        message: The error message for status description
    """

    exit_code: int = 1
    message: str = "Execution Failed"

    def __init__(self, message: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Optional message that will be appended to the default message.

        Note:
            To return result data with errors, use error_manager.set_result()
            before raising the exception.
        """
        if message:
            self.message = f"{self.message}: {message}"

        super().__init__(self.message)


class DataValidationError(ExecutionError):
    """Raised when an input field is invalid."""
    exit_code = 20
    message = "Data Validation Error"


class UnexpectedSystemError(ExecutionError):
    """Raised for unexpected system errors."""
    exit_code = 1
    message = "System Error"


class ValidationError(ExecutionError):
    """
    Raised when a required input field is missing or contains an invalid value.

    Use this before any S3 API calls when validating user-supplied field values
    such as aws_region, bucket_name, local_file, or s3_object_key.

    Exit code 20 signals a user configuration error to UAC.
    """
    exit_code = 20
    message = "Validation Error"


class AuthenticationError(ExecutionError):
    """
    Raised when AWS authentication or authorization fails.

    Use this when botocore raises a ClientError whose error code indicates an
    invalid, expired, or insufficient credential:
      - InvalidClientTokenId
      - AuthFailure
      - AccessDenied
      - ExpiredToken
      - InvalidAccessKeyId

    These errors are non-transient — they require credential correction or an
    IAM policy update before a retry will succeed.
    """
    exit_code = 1
    message = "Authentication Error"


class BucketNotFoundError(ExecutionError):
    """
    Raised when the specified S3 bucket does not exist or is not accessible
    in the configured region.

    Use this when botocore raises a ClientError with error code NoSuchBucket,
    or when an equivalent access-denied response indicates the bucket cannot
    be reached.

    This is a user configuration error — the bucket name or region must be
    corrected before a retry will succeed.
    """
    exit_code = 1
    message = "Bucket Not Found"


class LocalFileNotFoundError(ExecutionError):
    """
    Raised when the local file specified for upload does not exist or is not
    accessible on the Universal Agent host filesystem at execution time.

    Use this before initiating an S3 upload when os.path.isfile returns False
    for the provided local_file path, or when boto3 raises a FileNotFoundError
    during upload_file.

    This is a user input error — the local_file field must reference an
    existing, readable file path.
    """
    exit_code = 1
    message = "Local File Not Found"


class S3OperationError(ExecutionError):
    """
    Raised when an S3 API call or network operation fails for reasons other
    than authentication or a missing bucket.

    Use this for:
      - Network-level failures (connection timeout, SSL error, connection refused)
      - S3 throttling responses (SlowDown, RequestLimitExceeded)
      - Unexpected ClientError codes not classified as authentication or
        bucket-not-found errors

    These errors may be transient (throttling, timeouts); however no automatic
    retry is implemented for this MVP scope.
    """
    exit_code = 1
    message = "S3 Operation Error"
