## Issue: Test_AwsObjectStorage_ListObjects_LargeOutputCap

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains ASCII table with up to 500 rows
- No truncation notice appears if bucket has 500 or fewer total objects
- object_count output field reflects the actual total count in the bucket

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791230681989013155JF087YA0IM7QG

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
