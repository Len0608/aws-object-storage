## Issue: Test_AwsObjectStorage_ListObjects_MaxOutputRecords

**Status**: ⚠ Error

### Expected:
List objects in an S3 bucket with UE_MAX_OUTPUT_RECORDS capped at 5. Exit code 0, STDOUT output with object listing limited to 5 records.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE
statusDescription: Python requirements not satisfied: >=3.14
