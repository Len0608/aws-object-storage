## Issue: Test_AwsObjectStorage_UploadFile_RootKey

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains upload confirmation
- s3_uri output field is set to "s3://ue-test-bucket-20261005/test-upload-root.csv"
- File is placed at the root level of the bucket with no subdirectory prefix

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791230681989055155AKTOGB9B3LPTP

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
