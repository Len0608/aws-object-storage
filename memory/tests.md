# Test Plan

**Extension:** aws-object-storage
**Generated:** 2026-10-05

---

## Test: Test_AwsObjectStorage_ListObjects_Minimal

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains an ASCII table with columns: Object Key, Size (bytes), Last Modified (or empty bucket message if bucket is empty)
- object_count output field is populated with the total number of objects as a string
- Status description contains "Listed <N> objects in bucket 'ue-test-bucket-20261005'"

---

## Test: Test_AwsObjectStorage_ListObjects_MaxOutputRecords

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 5
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains an ASCII table with at most 5 rows
- If bucket has more than 5 objects, truncation notice is present: "Showing 5 of <N> objects. Set UE_MAX_OUTPUT_RECORDS to display more."
- object_count output field reflects the full total count, not the capped display count

---

## Test: Test_AwsObjectStorage_UploadFile_Minimal

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
- local_file: /tmp/ue-test-input/test-upload.csv
- s3_object_key: uploads/test-upload-minimal.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains upload confirmation including local file path, S3 URI, and file size in bytes
- s3_uri output field is set to "s3://ue-test-bucket-20261005/uploads/test-upload-minimal.csv"
- Status description: "Uploaded '/tmp/ue-test-input/test-upload.csv' to s3://ue-test-bucket-20261005/uploads/test-upload-minimal.csv"

---

## Test: Test_AwsObjectStorage_UploadFile_NestedPath

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
- local_file: /tmp/ue-test-input/test-upload.csv
- s3_object_key: data/2026/10/test-upload.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains upload confirmation with nested S3 URI
- s3_uri output field is set to "s3://ue-test-bucket-20261005/data/2026/10/test-upload.csv"
- File is placed at the deeply nested key within the bucket

---

## Test: Test_AwsObjectStorage_UploadFile_RootKey

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Input Fields:**
- action: Upload File
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
- local_file: /tmp/ue-test-input/test-upload.csv
- s3_object_key: test-upload-root.csv
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains upload confirmation
- s3_uri output field is set to "s3://ue-test-bucket-20261005/test-upload-root.csv"
- File is placed at the root level of the bucket with no subdirectory prefix

---

## Test: Test_AwsObjectStorage_ListObjects_LargeOutputCap

**Template:** Aws Object Storage
**Agent:** nginx-with-sidecar - AKS-SIDECAR-TEST
**Environment Variables:**
- UE_MAX_OUTPUT_RECORDS: 500
**Input Fields:**
- action: List Objects
- aws_credentials: aws-s3-test-credentials
- aws_region: us-east-1
- bucket_name: ue-test-bucket-20261005
**Expected Results:**
- Task completes with exit code 0
- STDOUT contains ASCII table with up to 500 rows
- No truncation notice appears if bucket has 500 or fewer total objects
- object_count output field reflects the actual total count in the bucket

---
