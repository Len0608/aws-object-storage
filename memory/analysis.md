# AWS Object Storage - Implementation Analysis

**Extension Name:** *AWS Object Storage (aws-object-storage)*
**Universal Template Name:** *Aws Object Storage*
**Target Platform:** Linux

---

## Extension Overview

The AWS Object Storage Universal Extension provides an MVP-level integration with Amazon S3, enabling UAC tasks to perform two core operations from a Linux Universal Agent host: listing objects in an S3 bucket and uploading a local file to S3. Authentication is performed using an AWS Access Key pair stored in a UAC Credential field. All dependencies (`boto3`, `botocore`, `s3transfer`, `tabulate`) are bundled with the extension and require no manual installation on the agent host.

---

# Template Fields

## 1. Input Fields

**action**
- **Type**: Choice Field (Single-select)
- **Visible When**: always
- **Required When**: always
- **Options**:
  - `List Objects` - List all objects in the specified S3 bucket with key, size, and last-modified details
  - `Upload File` - Upload a local file from the agent host to a specified S3 bucket and object key
- **Default Value**: `List Objects`
- **Validation**:
  - Must be one of the defined options
- **Purpose**: Selects the S3 operation to perform

---

**aws_credentials**
- **Type**: Credential Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Credential must be provided
  - `user` attribute must contain the AWS Access Key ID
  - `password` attribute must contain the AWS Secret Access Key
- **Purpose**: Provides AWS authentication. The `user` attribute maps to the Access Key ID; the `password` attribute maps to the Secret Access Key. No other attributes are used.

---

**aws_region**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must be a non-empty string
  - Must be a valid AWS region identifier
- **Purpose**: The AWS region where the target S3 bucket resides. Used when constructing the S3 client to ensure the correct regional endpoint is used.
- **Example**: `us-east-1`

---

**bucket_name**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must be a non-empty string
  - Must not contain leading or trailing whitespace
- **Purpose**: The name of the S3 bucket to operate on. Applies to both List Objects and Upload File actions.
- **Example**: `my-demo-bucket`

---

**local_file**
- **Type**: Text Field
- **Visible When**: `action` value is equal to `Upload File`. It is required when it is visible.
- **Required When**: `action` value is equal to `Upload File`
- **Validation**:
  - Must be a non-empty absolute path string
  - Must reference an existing, readable file on the agent host filesystem at execution time
- **Purpose**: The absolute path to the file on the Universal Agent host to be uploaded to S3.
- **Example**: `/tmp/report-2026.csv`

---

**s3_object_key**
- **Type**: Text Field
- **Visible When**: `action` value is equal to `Upload File`. It is required when it is visible.
- **Required When**: `action` value is equal to `Upload File`
- **Validation**:
  - Must be a non-empty string
  - Must not begin with a forward slash (S3 object keys are relative paths within the bucket)
- **Purpose**: The destination key (path) within the S3 bucket under which the file will be stored. The file is placed at exactly this key.
- **Example**: `uploads/report-2026.csv`

---

## 2. Output Fields

**object_count**
- **Type**: Text Output
- **Visible When**: `action` is `List Objects`
- **Purpose**: Displays the total number of objects found in the S3 bucket after the List Objects action completes. This is the actual S3 count, not the capped displayed count.
- **Examples**: `"4832"`, `"0"`, `"100"`

---

**s3_uri**
- **Type**: Text Output
- **Visible When**: `action` is `Upload File`
- **Purpose**: Displays the full `s3://bucket-name/object-key` URI of the file that was successfully uploaded, providing an at-a-glance reference to the destination in the UAC task panel.
- **Examples**: `"s3://my-demo-bucket/uploads/report-2026.csv"`, `"s3://my-demo-bucket/data/archive.tar.gz"`

---

## 3. Field Ordering

The task form uses a **2-column grid layout**. All fields in this extension span full-width due to their primary selection and connection nature. Upload-specific fields appear below the shared connection fields and are hidden when the action is List Objects.

**Field Order (Visual Layout):**

```
┌─────────────────────────────────────────┐
│                  action                 │  ← Full-width (primary selector)
├─────────────────────────────────────────┤
│             aws_credentials             │  ← Full-width (credential)
├─────────────────────────────────────────┤
│               aws_region                │  ← Full-width
├─────────────────────────────────────────┤
│              bucket_name                │  ← Full-width
├─────────────────────────────────────────┤
│              local_file                 │  ← Full-width (Upload File only)
├─────────────────────────────────────────┤
│             s3_object_key               │  ← Full-width (Upload File only)
├─────────────────────────────────────────┤
│              object_count               │  ← Full-width (Output Only)
├─────────────────────────────────────────┤
│                s3_uri                   │  ← Full-width (Output Only)
└─────────────────────────────────────────┘
```

---

# Actions

## Action 1: List Objects

**Description**: Retrieves all objects from the specified S3 bucket using paginated API calls. Renders the results as an ASCII table on STDOUT. Caps the number of records written to STDOUT and Extension Output JSON at `UE_MAX_OUTPUT_RECORDS` (default: 100). The actual S3 API listing is not capped. Sets the `object_count` output field with the total object count.

### Input Requirements

- **action** — must be `List Objects`
- **aws_credentials** — provides Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — AWS region for S3 client construction
- **bucket_name** — target S3 bucket name

### Execution Flow

**Step 1: Input Validation**
- Verify `aws_credentials` is provided (non-None)
- Verify `aws_region` is non-empty
- Verify `bucket_name` is non-empty
- If any validation fails: raise `ValidationError` with a descriptive message identifying the missing field; exit code 20

**Step 2: Read Output Cap**
- Read environment variable `UE_MAX_OUTPUT_RECORDS`
- If not set or not a valid positive integer: use default value `100`

**Step 3: Construct S3 Client**
- Create boto3 S3 client using:
  - `aws_access_key_id` = `input_data.aws_credentials.user`
  - `aws_secret_access_key` = `input_data.aws_credentials.password`
  - `region_name` = `input_data.aws_region`
- Wrap the client creation and all subsequent S3 calls in a try/finally block to guarantee client cleanup after execution

**Step 4: Paginate and Collect All Objects**
- Use the boto3 paginator for `list_objects_v2` with `Bucket=bucket_name`
- Iterate through all pages and accumulate every object's metadata:
  - `key`: the object's `Key`
  - `size`: the object's `Size` in bytes
  - `last_modified`: the object's `LastModified` timestamp formatted as ISO 8601 UTC string (e.g., `2026-09-15T10:22:43Z`)
- Track the total count of all objects retrieved across all pages
- If the bucket does not exist or is inaccessible: catch the boto3/botocore `ClientError` and raise `BucketNotFoundError` or `AuthenticationError` as appropriate (see Exception Mapping Strategy)
- If any other S3/network error occurs: raise `S3OperationError`

**Step 5: Apply Output Cap**
- Select the first `min(total_count, max_output_records)` objects for display — this is `displayed_count`
- Remaining objects beyond the cap are discarded from the output only; the total count is retained

**Step 6: Render STDOUT**
- Format the capped list of objects as an ASCII table using the `tabulate` library with `tablefmt="rounded_outline"`
- Columns: `Object Key`, `Size (bytes)`, `Last Modified`
- Print the table to STDOUT
- If `displayed_count < total_count`: print a truncation notice immediately after the table:
  `Showing <displayed_count> of <total_count> objects. Set UE_MAX_OUTPUT_RECORDS to display more.`
- If the bucket is empty (total_count = 0): print a message indicating the bucket is empty rather than an empty table

**Step 7: Set Output Field**
- Set `output_data.object_count` to the string representation of `total_count`

**Step 8: Return Result**
- Return exit code `0`
- Status description: `Listed <total_count> objects in bucket '<bucket_name>'`
- Extension Output JSON `result` object as defined in Output Examples

**Step 9: Cleanup (always)**
- In the finally block: close the boto3 S3 client's HTTP session to release connections

### Output Examples

**STDOUT** (when 4832 total objects, cap at 100):
```
╭────────────────────────────┬──────────────┬──────────────────────────╮
│ Object Key                 │ Size (bytes) │ Last Modified            │
├────────────────────────────┼──────────────┼──────────────────────────┤
│ data/report.csv            │ 142308       │ 2026-09-15T10:22:43Z     │
│ data/archive.tar.gz        │ 8192000      │ 2026-09-20T08:11:05Z     │
│ ...                        │ ...          │ ...                      │
╰────────────────────────────┴──────────────┴──────────────────────────╯
Showing 100 of 4832 objects. Set UE_MAX_OUTPUT_RECORDS to display more.
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "bucket": "my-bucket",
    "total_count": 4832,
    "displayed_count": 100,
    "objects": [
      {"key": "data/report.csv", "size": 142308, "last_modified": "2026-09-15T10:22:43Z"},
      {"key": "data/archive.tar.gz", "size": 8192000, "last_modified": "2026-09-20T08:11:05Z"}
    ]
  }
}
```

*Note: The `objects` array contains exactly `displayed_count` entries. `total_count` always reflects the actual S3 object count regardless of the cap. The Extension Output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation.*

### Success Criteria

1. The S3 `list_objects_v2` paginated call completes without error across all pages
2. The `object_count` output field is set to the total object count as a string
3. STDOUT contains a properly formatted ASCII table (or empty bucket message)
4. If output was truncated, the truncation notice is present in STDOUT
5. Extension Output JSON is emitted with the correct structure (`bucket`, `total_count`, `displayed_count`, `objects`)
6. Return code is `0`

---

## Action 2: Upload File

**Description**: Uploads a local file from the Universal Agent host filesystem to a specified S3 bucket and object key. Confirms the upload on STDOUT. Populates the `s3_uri` output field with the full S3 URI of the uploaded object. Emits Extension Output JSON with bucket name, key, URI, and file size.

### Input Requirements

- **action** — must be `Upload File`
- **aws_credentials** — provides Access Key ID (`user`) and Secret Access Key (`password`)
- **aws_region** — AWS region for S3 client construction
- **bucket_name** — target S3 bucket name
- **local_file** — absolute path to the file on the agent host
- **s3_object_key** — destination key within the S3 bucket

### Execution Flow

**Step 1: Input Validation**
- Verify `aws_credentials` is provided (non-None)
- Verify `aws_region` is non-empty
- Verify `bucket_name` is non-empty
- Verify `local_file` is non-empty
- Verify `s3_object_key` is non-empty
- If any field is missing: raise `ValidationError` with a descriptive message; exit code 20
- Verify that the file at `local_file` path exists and is accessible on the agent filesystem
- If the file does not exist: raise `LocalFileNotFoundError` with message `Local file not found: <local_file_path>`; exit code 1

**Step 2: Retrieve File Size**
- Read the size of the local file in bytes using the filesystem metadata
- Store as `file_size_bytes` — this is used in output after upload

**Step 3: Construct S3 Client**
- Create boto3 S3 client using:
  - `aws_access_key_id` = `input_data.aws_credentials.user`
  - `aws_secret_access_key` = `input_data.aws_credentials.password`
  - `region_name` = `input_data.aws_region`
- Wrap the client creation and all subsequent S3 calls in a try/finally block to guarantee client cleanup after execution

**Step 4: Upload File to S3**
- Use the boto3 S3 client's `upload_file` method with:
  - `Filename` = `local_file` (absolute path)
  - `Bucket` = `bucket_name`
  - `Key` = `s3_object_key`
- The file is placed at the exact `s3_object_key` specified — no path manipulation is performed
- If authentication fails or permissions are insufficient: catch the botocore `ClientError` and raise `AuthenticationError`
- If the bucket does not exist or is inaccessible: catch the botocore `ClientError` and raise `BucketNotFoundError`
- If any other S3/network error occurs: raise `S3OperationError`

**Step 5: Compose S3 URI**
- Construct the full S3 URI: `s3://<bucket_name>/<s3_object_key>`

**Step 6: Render STDOUT**
- Print a human-readable upload confirmation message:
  ```
  Upload successful.
    Local file : <local_file>
    S3 URI     : s3://<bucket_name>/<s3_object_key>
    File size  : <file_size_bytes> bytes
  ```

**Step 7: Set Output Field**
- Set `output_data.s3_uri` to the full S3 URI string

**Step 8: Return Result**
- Return exit code `0`
- Status description: `Uploaded '<local_file>' to s3://<bucket_name>/<s3_object_key>`
- Extension Output JSON `result` object as defined in Output Examples

**Step 9: Cleanup (always)**
- In the finally block: close the boto3 S3 client's HTTP session to release connections

### Output Examples

**STDOUT**:
```
Upload successful.
  Local file : /tmp/report-2026.csv
  S3 URI     : s3://my-bucket/uploads/report-2026.csv
  File size  : 142308 bytes
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "bucket": "my-bucket",
    "key": "uploads/report-2026.csv",
    "s3_uri": "s3://my-bucket/uploads/report-2026.csv",
    "size_bytes": 142308
  }
}
```

*Note: The Extension Output also includes `exit_code`, `status_description`, and `invocation` elements added automatically during implementation.*

### Success Criteria

1. The local file exists and is accessible at the specified path before the upload begins
2. The boto3 `upload_file` call completes without error
3. The `s3_uri` output field is populated with the full S3 URI
4. STDOUT contains the upload confirmation message with local file path, S3 URI, and file size
5. Extension Output JSON is emitted with the correct structure (`bucket`, `key`, `s3_uri`, `size_bytes`)
6. Return code is `0`

---

# Progress Reporting

Progress Reporting (percentage of completion report) is not required. Both actions produce a single STDOUT output upon completion. No intermediate progress updates are emitted during execution.

---

# Dynamic Choice Field Population

No Dynamic choice fields should be implemented. All choice fields in this extension use fixed, statically defined option sets.

---

# Cancellation Behavior

Default UAC task cancellation behavior applies (TERM signal). No custom cancellation logic is required. The boto3 S3 client will be left without explicit cleanup if a TERM signal is received mid-operation; this is acceptable for this MVP scope.

---

# Re-Run Behavior

Re-runs are treated as initial executions. Both actions are idempotent with respect to S3 state:
- **List Objects** is read-only and always returns the current bucket state
- **Upload File** overwrites an existing object at the same key with the new file contents

No output field values from a previous run are used to alter re-run behavior.

---

# Dynamic Commands

No Dynamic commands should be implemented.

---

# Utility Modules

## Required Utility Modules

### 1. S3ClientFactory

**Purpose:** Constructs and manages the lifecycle of the boto3 S3 client. Centralizes client creation to ensure credentials are applied consistently and the HTTP session is closed after use.

**Required Capabilities:**
- Accept AWS Access Key ID, AWS Secret Access Key, and AWS region as inputs
- Construct and return a configured boto3 S3 client
- Provide a method to close the client's underlying HTTP session (releasing connections) — this is invoked in the finally block of each action

**Used By:** List Objects action, Upload File action

---

### 2. S3Operations

**Purpose:** Encapsulates the S3 API calls for the two supported operations. Translates botocore/boto3 `ClientError` exceptions into domain-specific extension exceptions.

**Required Capabilities:**

**List Objects:**
- Use the boto3 paginator for `list_objects_v2` to iterate through all pages of a bucket
- Accumulate object metadata (key, size, last_modified as ISO 8601 UTC string) from every page
- Return the full list of object metadata dicts and the total count
- Classify `ClientError` by error code: `InvalidClientTokenId` / `AuthFailure` / `AccessDenied` → `AuthenticationError`; `NoSuchBucket` / `NoSuchKey` → `BucketNotFoundError`; all others → `S3OperationError`

**Upload File:**
- Call boto3 `upload_file` with local file path, bucket name, and S3 object key
- Classify `ClientError` using the same error code mapping as above
- Propagate `FileNotFoundError` from boto3 as `LocalFileNotFoundError`

**Error Classification:**
- `ClientError` codes `InvalidClientTokenId`, `AuthFailure`, `AccessDenied`, `ExpiredToken`, `InvalidAccessKeyId` → `AuthenticationError`
- `ClientError` code `NoSuchBucket` → `BucketNotFoundError`
- `ClientError` codes for throttling (`SlowDown`, `RequestLimitExceeded`) or other service errors → `S3OperationError`
- Network-level errors (connection timeout, SSL error) → `S3OperationError`

**Used By:** List Objects action, Upload File action

---

### 3. OutputFormatter

**Purpose:** Formats the list objects result as an ASCII table for STDOUT and constructs the Extension Output JSON result objects for both actions.

**Required Capabilities:**

**Table Rendering:**
- Accept a list of object metadata dicts and format them as an ASCII table using `tabulate` with `tablefmt="rounded_outline"`
- Column headers: `Object Key`, `Size (bytes)`, `Last Modified`
- If the list is empty, return a human-readable message indicating the bucket contains no objects

**Truncation Notice:**
- Accept `displayed_count` and `total_count`; return the truncation notice string when `displayed_count < total_count`

**Result Object Construction:**
- Build the `result` dict for List Objects: `{"bucket": str, "total_count": int, "displayed_count": int, "objects": list[dict]}`
- Build the `result` dict for Upload File: `{"bucket": str, "key": str, "s3_uri": str, "size_bytes": int}`
- Build the STDOUT confirmation string for Upload File including local path, S3 URI, and file size

**Used By:** List Objects action, Upload File action

---

## Exception Mapping Strategy

**Authentication and Authorization Errors:**
- Invalid Access Key ID or expired credentials → `AuthenticationError` (exit code 1, non-transient — requires credential correction)
- Insufficient IAM permissions for the S3 operation → `AuthenticationError` (exit code 1, non-transient — requires IAM policy update)

**Resource Errors:**
- Bucket does not exist or is not accessible in the specified region → `BucketNotFoundError` (exit code 1, user configuration error)
- Local file path does not exist on agent filesystem at execution time → `LocalFileNotFoundError` (exit code 1, user input error)

**S3 Service and Network Errors:**
- Network timeout, connection refused, SSL error → `S3OperationError` (exit code 1, potentially transient)
- S3 throttling (`SlowDown`) → `S3OperationError` (exit code 1, transient — no retry implemented for MVP)
- Unexpected S3 API error → `S3OperationError` (exit code 1, system error)

**Input Validation Errors:**
- Missing required field value (credential not provided, empty region, empty bucket name, empty local file path, empty S3 object key) → `ValidationError` (exit code 20, user configuration error)

**Exit Code Guide:**
- Exit code 0: Successful execution
- Exit code 1: Operational failure (authentication, resource access, S3 service/network, local file not found)
- Exit code 20: Input validation failure (missing or invalid required field values before any S3 call)

---

# Dependencies

## 1. External API Dependencies

**1. Amazon S3 API**
- **Endpoint**: `https://s3.<region>.amazonaws.com` (resolved automatically by boto3 based on the region parameter)
- **Purpose**: Core S3 service used for listing objects and uploading files
- **Protocol**: HTTPS
- **Method**: Multiple (GET for list, PUT for upload — handled transparently by boto3)
- **Authentication**: AWS Signature Version 4 — performed automatically by boto3 using the provided Access Key ID and Secret Access Key
- **Response Format**: XML (parsed transparently by boto3 into Python dicts)
- **Data Retrieved/Sent**: Object metadata (key, size, last_modified) for listing; binary file data for upload

**General API Requirements:**
- An AWS account with a valid IAM user or role possessing `s3:ListBucket` permission for List Objects and `s3:PutObject` permission for Upload File on the target bucket
- Access Key ID and Secret Access Key for the IAM principal with the above permissions
- No special API activation steps beyond standard AWS account setup

---

## 2. Python version dependency

Python >= 3.11 (as configured in the extension workspace)

---

## 3. Target Platform

Linux only (manylinux_2_17_x86_64). C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules. All selected dependencies (`boto3`, `botocore`, `s3transfer`, `tabulate`) are pure-Python and are fully compatible with this target.

---

## 4. Python Library Dependencies

**1. boto3**
- **Purpose**: AWS SDK for Python; provides the high-level S3 client used for all S3 operations (`list_objects_v2` via paginator, `upload_file`)
- **Version**: `==1.43.108`
- **Installation**: `pip install boto3==1.43.108`
- **Usage**: S3ClientFactory and S3Operations utilities
- **Features Used**: `boto3.client('s3', ...)`, `client.get_paginator('list_objects_v2')`, `client.upload_file()`

**2. botocore**
- **Purpose**: Low-level AWS service client library; core dependency of boto3 handling request signing, retries, and protocol handling. Also provides the `ClientError` exception class used for error classification.
- **Version**: `==1.43.108`
- **Installation**: `pip install botocore==1.43.108` (installed as transitive dependency of boto3)
- **Usage**: S3Operations utility for `ClientError` exception handling
- **Features Used**: `botocore.exceptions.ClientError`

**3. s3transfer**
- **Purpose**: Managed multipart S3 transfer library; core dependency of boto3 for efficient file uploads
- **Version**: `==0.19.2`
- **Installation**: `pip install s3transfer==0.19.2` (installed as transitive dependency of boto3)
- **Usage**: Used transparently by boto3's `upload_file` method
- **Features Used**: Transparent multipart upload management

**4. tabulate**
- **Purpose**: Formats data as clean ASCII tables for STDOUT output; used to render the object listing in `rounded_outline` style
- **Version**: `==0.10.0`
- **Installation**: `pip install tabulate==0.10.0`
- **Usage**: OutputFormatter utility for the List Objects action
- **Features Used**: `tabulate(data, headers=..., tablefmt="rounded_outline")`

---

## 5. Python Standard Library Dependencies

**1. os**
- **Purpose**: Filesystem operations
- **Version**: Standard library (Python 3.11)
- **Installation**: Built-in, no installation required
- **Usage**: Check file existence (`os.path.isfile`), retrieve file size (`os.path.getsize`)
- **Features Used**: `os.path.isfile`, `os.path.getsize`

**2. json**
- **Purpose**: JSON serialization for Extension Output
- **Version**: Standard library (Python 3.11)
- **Installation**: Built-in
- **Usage**: OutputFormatter utility for building Extension Output JSON
- **Features Used**: `json.dumps`

**3. datetime**
- **Purpose**: Timestamp formatting
- **Version**: Standard library (Python 3.11)
- **Installation**: Built-in
- **Usage**: S3Operations utility to format `LastModified` datetime objects to ISO 8601 UTC strings
- **Features Used**: `datetime.strftime` or `.isoformat()`

---

## 6. CLI Tool Dependencies

No Dependencies. All S3 operations are performed via the bundled `boto3` Python SDK. No CLI tools are required to be pre-installed on the agent host.

---

## 7. Environment Variables

**`UE_MAX_OUTPUT_RECORDS`** (integer, optional):
- **Purpose**: Caps the number of S3 objects written to STDOUT and the `objects` array in Extension Output JSON for the List Objects action. Does not limit the actual S3 API call or affect the `total_count` value.
- **Default**: `100`
- **Usage**: Read at the start of the List Objects action execution. If the variable is absent or not a valid positive integer, the default of `100` is used silently.
- **Examples**: `50`, `200`, `500`
