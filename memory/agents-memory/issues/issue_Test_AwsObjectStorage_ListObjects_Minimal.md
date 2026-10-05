## Issue: Test_AwsObjectStorage_ListObjects_Minimal

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains an ASCII table with columns: Object Key, Size (bytes), Last Modified (or empty bucket message if bucket is empty)
- object_count output field is populated with the total number of objects as a string
- Status description contains "Listed <N> objects in bucket 'ue-test-bucket-20261005'"

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791219315338813155F616LN68GHP6T

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
