## Issue: Test_AwsObjectStorage_UploadFile_Minimal

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains upload confirmation including local file path, S3 URI, and file size in bytes
- s3_uri output field is set to "s3://ue-test-bucket-20261005/uploads/test-upload-minimal.csv"
- Status description: "Uploaded '/tmp/ue-test-input/test-upload.csv' to s3://ue-test-bucket-20261005/uploads/test-upload-minimal.csv"

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791230681989026155O4UUMTO9T983K

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
