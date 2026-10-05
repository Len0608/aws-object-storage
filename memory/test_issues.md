# Test Issues Log

All 6 tasks failed with START FAILURE status.

## Common Root Cause

**statusDescription**: Python requirements not satisfied: >=3.14

The extension requires Python >= 3.14, but the agent `nginx-with-sidecar - AKS-SIDECAR-TEST` does not satisfy this requirement. No STDOUT or STDERR was produced for any task.

---

## Issue: Test_AwsObjectStorage_ListObjects_Minimal

**Status**: ⚠ Error

### Expected:
List all objects in an S3 bucket with minimal required inputs. Exit code 0, STDOUT output with object listing.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791219315338813155F616LN68GHP6T

---

## Issue: Test_AwsObjectStorage_ListObjects_MaxOutputRecords

**Status**: ⚠ Error

### Expected:
List objects with UE_MAX_OUTPUT_RECORDS capped at 5. Exit code 0, STDOUT output with object listing limited to 5 records.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791219315338898155DUUSTZ3QMUM83

---

## Issue: Test_AwsObjectStorage_ListObjects_LargeOutputCap

**Status**: ⚠ Error

### Expected:
List objects with UE_MAX_OUTPUT_RECORDS capped at 500. Exit code 0, STDOUT output with object listing.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791230681989013155JF087YA0IM7QG

---

## Issue: Test_AwsObjectStorage_UploadFile_Minimal

**Status**: ⚠ Error

### Expected:
Upload a local file to S3 at a simple path. Exit code 0, STDOUT confirmation of successful upload.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791230681989026155O4UUMTO9T983K

---

## Issue: Test_AwsObjectStorage_UploadFile_NestedPath

**Status**: ⚠ Error

### Expected:
Upload a local file to S3 at a deeply nested key path. Exit code 0, STDOUT confirmation of successful upload.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791230681989039155EYW6M6X4Q12G6

---

## Issue: Test_AwsObjectStorage_UploadFile_RootKey

**Status**: ⚠ Error

### Expected:
Upload a local file to S3 at root level with no subdirectory prefix. Exit code 0, STDOUT confirmation of successful upload.

### STDOUT:
[empty]

### STDERR:
[empty]

### Extension Output:
statusCode: START FAILURE  
statusDescription: Python requirements not satisfied: >=3.14  
Instance SysID: 1791230681989055155AKTOGB9B3LPTP
