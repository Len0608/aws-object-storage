## Issue: Test_AwsObjectStorage_ListObjects_MaxOutputRecords

**Status**: ⚠ Error

### Expected:
- Task completes with exit code 0
- STDOUT contains an ASCII table with at most 5 rows
- If bucket has more than 5 objects, truncation notice is present: "Showing 5 of <N> objects. Set UE_MAX_OUTPUT_RECORDS to display more."
- object_count output field reflects the full total count, not the capped display count

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
Status: START FAILURE
StatusDescription: Python requirements not satisfied: >=3.14
ExitCode: 0
Instance SysId: 1791219315338898155DUUSTZ3QMUM83

The task did not execute. The UAC agent (nginx-with-sidecar - AKS-SIDECAR-TEST) does not meet the Python version requirement (>=3.14) specified in the extension's extension.yml.
