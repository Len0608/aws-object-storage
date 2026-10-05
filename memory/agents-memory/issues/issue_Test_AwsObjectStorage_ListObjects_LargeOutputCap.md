## Issue: Test_AwsObjectStorage_ListObjects_LargeOutputCap

**Status**: ⚠ Error

### Expected:
Task executes successfully against action "List Objects" with UE_MAX_OUTPUT_RECORDS=500, AWS credentials, region us-east-1, bucket ue-test-bucket-20261005. Output should return up to 500 S3 objects.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE
statusDescription: Python requirements not satisfied: >=3.14
