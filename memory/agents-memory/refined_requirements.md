# Universal Extension Requirements (Refined)

**Extension Name:** AWS Object Storage
**Original Generated:** Not specified in source document
**Refined:** 2026-10-05
**Agent_id:** Not specified in source document
**Requirements Completeness:** High Detail
**Target Platform:** Linux

---

# Table of Contents

1. [Overview](#overview)
2. [Actions](#actions)
   - 2.1 [Action 1 — List Objects](#action-1--list-objects)
   - 2.2 [Action 2 — Upload File](#action-2--upload-file)
3. [Input Requirements](#input-requirements)
   - 3.1 [Connection Parameters](#31-connection-parameters)
   - 3.2 [List Objects Parameters](#32-list-objects-parameters)
   - 3.3 [Upload File Parameters](#33-upload-file-parameters)
4. [Output Requirements](#output-requirements)
   - 4.1 [On Success](#41-on-success)
   - 4.2 [On Error](#42-on-error)
5. [Authentication Requirements](#authentication-requirements)
6. [Environment Variables](#environment-variables)
7. [Operational Behavior](#operational-behavior)
8. [Implementation Notes](#implementation-notes)
   - 8.1 [Python Compatibility](#81-python-compatibility)
   - 8.2 [Target Platform](#82-target-platform)
   - 8.3 [Third-Party Services and Tools](#83-third-party-services-and-tools)
   - 8.4 [Error Handling](#84-error-handling)
   - 8.5 [Resource Cleanup](#85-resource-cleanup)
9. [Requirements Summary](#requirements-summary)
10. [Document Change History](#document-change-history)
11. [References](#references)

---

# Overview

This document defines the requirements for a Stonebranch Universal Extension named **AWS Object Storage**, providing an MVP-level integration with Amazon S3 to demonstrate that S3 operations can be executed from Universal Automation Center (UAC).

**Integration Purpose:** Enable UAC tasks to perform two S3 operations — listing objects in a bucket and uploading a local file from the Universal Agent host to a specified S3 location — using the `boto3` Python SDK bundled within the extension.

---

# Actions

## Action 1 — List Objects

**Functional Requirements:**

1. The extension must list all objects in a specified S3 bucket.
2. The listing must retrieve, for each object: the object key, the object size in bytes, and the last-modified timestamp.
3. The number of objects written to STDOUT and Extension Output JSON must be capped by the `UE_MAX_OUTPUT_RECORDS` environment variable (default: 100). The actual S3 listing operation is not capped.
4. When the result set exceeds the cap, the output must include a truncation notice stating the total count and the applied limit.
5. The total object count must be included in Extension Output JSON regardless of whether the output was truncated.
6. The output-only field `Object Count` must be populated with the total number of objects found in the bucket.
7. STDOUT must render the listed objects as an ASCII table with columns: `Object Key`, `Size (bytes)`, and `Last Modified`.

## Action 2 — Upload File

**Functional Requirements:**

1. The extension must upload a local file from the Universal Agent host to a specified S3 bucket and S3 object key.
2. The local file path must resolve to a file accessible on the filesystem of the Universal Agent host.
3. The upload must place the file at the exact S3 object key specified in the input.
4. Upon successful upload, the extension must populate the `S3 URI` output-only field with the full `s3://bucket-name/object-key` URI of the uploaded object.
5. The Extension Output JSON must include the bucket name, the S3 object key, the full S3 URI, and the size of the uploaded file in bytes.

---

# Input Requirements

## 3.1 Connection Parameters

These fields apply to both actions.

- **Action** (choice, required): Selects the operation to perform.
  - Available options: `List Objects`, `Upload File`
  - Default: `List Objects`
  - Applicability: All actions

- **AWS Credentials** (credential, required): UAC Credential field holding the AWS access key pair.
  - Applicability: All actions
  - The `user` attribute of the credential must contain the **AWS Access Key ID**.
  - The `password` attribute of the credential must contain the **AWS Secret Access Key**.

- **AWS Region** (text, required): The AWS region in which the target S3 bucket resides.
  - Example: `us-east-1`
  - Applicability: All actions

- **Bucket Name** (text, required): The name of the S3 bucket to operate on.
  - Example: `my-demo-bucket`
  - Applicability: All actions

## 3.2 List Objects Parameters

No additional input fields beyond the connection parameters are required for the List Objects action.

## 3.3 Upload File Parameters

These fields are shown only when the `Upload File` action is selected.

- **Local File** (text, required): The absolute path to the file on the Universal Agent host to be uploaded.
  - Example: `/tmp/report-2026.csv`
  - Applicability: Upload File only

- **S3 Object Key** (text, required): The destination key (path) under which the file will be stored in the S3 bucket.
  - Example: `uploads/report-2026.csv`
  - Applicability: Upload File only

---

# Output Requirements

## 4.1 On Success

### List Objects Action

- **Return code:** 0
- **Status description:** `Listed <total_count> objects in bucket '<bucket_name>'`
- **Output-only fields:**
  - `Object Count` (integer): Total number of objects found in the bucket
- **Extension Output JSON:**
  ```json
  {
    "result": {
      "bucket": "my-bucket",
      "total_count": 4832,
      "displayed_count": 100,
      "objects": [
        {"key": "data/report.csv", "size": 142308, "last_modified": "2026-09-15T10:22:43Z"},
        "..."
      ]
    }
  }
  ```
  - `total_count` reflects the actual S3 count regardless of the cap.
  - `displayed_count` reflects the number of objects included in the `objects` array (capped by `UE_MAX_OUTPUT_RECORDS`).
- **STDOUT output:** ASCII table using `rounded_outline` format with columns `Object Key`, `Size (bytes)`, `Last Modified`. When truncated, a note must follow the table:
  `Showing <displayed_count> of <total_count> objects. Set UE_MAX_OUTPUT_RECORDS to display more.`
- **Success Criteria:**
  1. The S3 API call completes without error.
  2. The output-only field `Object Count` is set.
  3. Extension Output JSON is emitted with the correct structure.
  4. STDOUT contains the ASCII table (and truncation notice if applicable).

### Upload File Action

- **Return code:** 0
- **Status description:** `Uploaded '<local_file>' to s3://<bucket_name>/<s3_object_key>`
- **Output-only fields:**
  - `S3 URI` (text): Full `s3://bucket-name/object-key` URI of the uploaded file
- **Extension Output JSON:**
  ```json
  {
    "result": {
      "bucket": "my-bucket",
      "key": "uploads/report.csv",
      "s3_uri": "s3://my-bucket/uploads/report.csv",
      "size_bytes": 142308
    }
  }
  ```
- **STDOUT output:** A confirmation message stating the local file path, the destination S3 URI, and the file size in bytes.
- **Success Criteria:**
  1. The file is successfully transferred to S3.
  2. The `S3 URI` output-only field is populated.
  3. Extension Output JSON is emitted with the correct structure.
  4. STDOUT contains the upload confirmation message.

## 4.2 On Error

**Failure Scenarios:**

- **Authentication Failure**
  - Description: Provided AWS credentials are invalid or lack permission for the requested S3 operation.
  - Root causes: Invalid Access Key ID, invalid Secret Access Key, insufficient IAM permissions.
  - Return code: Non-zero
  - Status description: `Authentication failed: <error_message>`

- **Bucket Not Found**
  - Description: The specified S3 bucket does not exist or is not accessible in the specified region.
  - Root causes: Incorrect bucket name, wrong region, bucket deleted, no access.
  - Return code: Non-zero
  - Status description: `Bucket not found: <bucket_name>`

- **Local File Not Found** (Upload File only)
  - Description: The file specified in the `Local File` field does not exist on the agent host.
  - Root causes: Incorrect path, file deleted before task execution.
  - Return code: Non-zero
  - Status description: `Local file not found: <local_file_path>`

- **S3 Operation Error**
  - Description: A generic S3 or network error occurs during the operation.
  - Root causes: Network timeout, S3 service error, throttling.
  - Return code: Non-zero
  - Status description: `S3 operation failed: <error_message>`

**STDERR requirements:** Error details and stack trace information must be written to STDERR.

**Input Validation:** Input field validation is required. Missing required fields must produce a clear error message before any S3 API call is attempted.

---

# Authentication Requirements

The extension must authenticate to AWS using **Access Key authentication**. The AWS Access Key ID is read from the `user` attribute of the UAC Credential field, and the AWS Secret Access Key is read from the `password` attribute. These values are passed directly to the `boto3` S3 client at construction time. No other authentication methods (e.g., IAM roles, session tokens) are required for this MVP.

---

# Environment Variables

- **`UE_MAX_OUTPUT_RECORDS`** (integer, optional): Caps the number of S3 objects written to STDOUT and Extension Output JSON for the List Objects action. Default value is `100`. This variable has no effect on the Upload File action and does not limit the actual S3 API call.

---

# Operational Behavior

**Dynamic Choice Fields:**
Not applicable. No dynamic choice fields are required for this extension.

**Cancel Action:**
Standard UAC task cancellation applies. No special cancel handling is required beyond what the UAC framework provides.

**Re-run Capability:**
The extension must support re-run via standard UAC mechanisms. Both actions are idempotent with respect to S3 state (listing is read-only; uploading overwrites an existing key with the same name).

**Progress Reporting:**
No progress bar or intermediate progress reporting is required. A single STDOUT output is produced upon completion of each action.

**Dynamic Commands:**
Not applicable. No dynamic commands are required for this extension.

---

# Implementation Notes

## 8.1 Python Compatibility

Not specified specifically. Targeting compatibility for 3.11.

## 8.2 Target Platform

Linux only (manylinux_2_17_x86_64). All Python dependencies must provide either a pure-Python wheel or a manylinux_2_17_x86_64-compatible wheel on PyPI. C-extension modules with a confirmed manylinux_2_17_x86_64 wheel are viable in addition to pure-Python modules.

## 8.3 Third-Party Services and Tools

**boto3 (v1.43.108)**
- Short Description: AWS SDK for Python; provides the high-level S3 client used for all S3 operations.
- Version constraints: 1.43.108
- Integration: Used to construct an S3 client with the provided credentials and region, and to perform `list_objects_v2` and `upload_file` API calls.
- Type: Pure Python

**botocore (v1.43.108)**
- Short Description: Low-level AWS service client library; core dependency of boto3 handling request signing, retries, and protocol handling.
- Version constraints: 1.43.108
- Integration: Installed as a transitive dependency of boto3.
- Type: Pure Python

**s3transfer (v0.19.2)**
- Short Description: Managed multipart S3 transfer library; core dependency of boto3 for efficient file uploads and downloads.
- Version constraints: 0.19.2
- Integration: Installed as a transitive dependency of boto3.
- Type: Pure Python

**tabulate (v0.10.0)**
- Short Description: Formats data as clean ASCII tables for STDOUT output; used to render the object listing in `rounded_outline` style.
- Version constraints: 0.10.0
- Integration: Used by the List Objects action to render the object table on STDOUT.
- Type: Pure Python

All dependencies must be bundled with the Universal Extension. Nothing may be installed separately on the Universal Agent host.

## 8.4 Error Handling

**Error categories:**
- Authentication errors (invalid credentials, permission denied)
- Resource errors (bucket not found, file not found)
- S3 service/network errors (timeouts, throttling, API errors)
- Input validation errors (missing required fields)

**Error handling strategy:** All errors must be caught and translated into a non-zero return code with a descriptive status message. Error details must be written to STDERR. The extension must not expose raw stack traces in the UAC status description.

**Recovery mechanisms:** None required for this MVP. No retry logic is specified.

## 8.5 Resource Cleanup

**Cleanup scenarios:** The boto3 S3 client session must be closed after the operation completes, whether on success or failure.

**Strategy:** Use standard Python resource management to ensure the S3 client is properly released after each task execution.

---

# Requirements Summary

The AWS Object Storage Universal Extension is an MVP-scoped integration that provides two S3 actions — **List Objects** and **Upload File** — executed from a Linux Universal Agent host. It authenticates using an AWS access key pair stored in a UAC Credential field (`user` = Access Key ID, `password` = Secret Access Key). All dependencies (`boto3`, `botocore`, `s3transfer`, `tabulate`) are pure-Python and must be bundled with the extension.

The List Objects action retrieves objects from a named S3 bucket, renders them as an ASCII table on STDOUT, applies a configurable record cap (`UE_MAX_OUTPUT_RECORDS`, default 100), and outputs the full object listing (up to the cap) plus total count in Extension Output JSON. An `Object Count` output-only field provides an at-a-glance count in the UAC task panel.

The Upload File action transfers a local file from the agent host to a specified S3 bucket and key, confirms the upload on STDOUT, and populates an `S3 URI` output-only field and Extension Output JSON with the destination URI and file size.

Input validation is required for all fields. Errors must produce descriptive non-zero exit codes and STDERR messages.

---

# Document Change History

- **2026-10-05 (original):** Initial requirements — High Detail. Core scope, actions, fields, and SDK clearly stated.
- **2026-10-05 (refined):** Comprehensive refinement based on 5 clarification questions and user feedback. Added: credential attribute mapping, STDOUT format (ASCII table with tabulate), record cap behavior (UE_MAX_OUTPUT_RECORDS), output-only field definitions (Object Count, S3 URI), Extension Output JSON structures for both actions, and dependency version confirmation.

---

# References

- Original Requirements Document: `memory/requirements.md`
- Original Requirements Q&A Document: `memory/agents-memory/requirements-QnA.md`
