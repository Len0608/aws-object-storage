"""
Utility package for the AWS Object Storage Universal Extension.

Exports:
    S3ClientFactory   - Constructs and manages the boto3 S3 client lifecycle
    S3Operations      - Encapsulates S3 API calls with domain-specific error mapping
    OutputFormatter   - Formats list/upload results for STDOUT and Extension Output JSON
"""
from utility.s3_client import S3ClientFactory
from utility.s3_operations import S3Operations
from utility.output_formatter import OutputFormatter

__all__ = ["S3ClientFactory", "S3Operations", "OutputFormatter"]
