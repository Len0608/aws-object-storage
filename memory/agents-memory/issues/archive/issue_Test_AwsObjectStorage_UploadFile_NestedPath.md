## Issue: Test_AwsObjectStorage_UploadFile_NestedPath

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains upload confirmation with nested S3 URI
- s3_uri output field is set to "s3://ue-test-bucket-20261005/data/2026/10/test-upload.csv"
- File is placed at the deeply nested key within the bucket

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791230681989039155EYW6M6X4Q12G6

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
