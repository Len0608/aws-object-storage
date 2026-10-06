> **Version:** 1.0.0 | **Date:** 2026-09-17

# AWS Object Storage — User Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Task Actions](#task-actions)
4. [Task Configuration](#task-configuration)
5. [Example Walkthroughs](#example-walkthroughs)
   - [Scenario 1: List all objects in a bucket](#scenario-1-list-all-objects-in-a-bucket)
   - [Scenario 2: Upload a local file to S3](#scenario-2-upload-a-local-file-to-s3)
6. [Troubleshooting](#troubleshooting)
7. [Field Reference](#field-reference)

---

## Overview

The **AWS Object Storage** Universal Extension integrates Stonebranch UAC with Amazon S3. It lets you automate two common S3 operations from within a UAC workflow:

- **List Objects** — retrieve the total count and details of all objects in a bucket.
- **Upload File** — push a local file from the agent host directly to an S3 bucket.

Output values (object count, uploaded S3 URI) are written back to the task record as structured extension output and are available to downstream workflow steps.

---

## Prerequisites

- A Stonebranch UAC agent (version 7.6.0.0 or later) deployed on the host that will run the task.
- An AWS IAM user or role with the appropriate permissions:
  - `s3:ListBucket` — required for **List Objects**.
  - `s3:PutObject` — required for **Upload File**.
- A UAC **Credential** entity configured with:
  - **Username** = AWS Access Key ID
  - **Password** = AWS Secret Access Key
- The target S3 bucket must already exist before the task runs.
- For **Upload File**: the file to be uploaded must be present on the agent host filesystem at the path you specify.

---

## Task Actions

### List Objects

Retrieves all objects from the specified S3 bucket using paginated `ListObjectsV2` API calls.

**When to use:** Use this action to audit bucket contents, count objects, or feed object metadata into downstream workflow steps.

**Execution flow:**

1. Input fields are validated (region, bucket name, credentials).
2. The extension authenticates to AWS using the provided credentials.
3. Paginated `ListObjectsV2` calls are made until all pages are retrieved.
4. The `object_count` output field is updated in real time as pages are processed.
5. The task completes with a structured result containing the total count and up to 100 object records (key, size, last modified). This cap is controlled by the `UE_MAX_OUTPUT_RECORDS` environment variable on the agent host (default: 100).

**Completion behavior:** The task exits with code `0` on success. The `object_count` field is visible in the task list view and is preserved on re-run.

---

### Upload File

Uploads a single file from the agent host to the specified S3 bucket.

**When to use:** Use this action to deliver build artifacts, reports, backups, or any file produced by an earlier workflow step to S3.

**Execution flow:**

1. Input fields are validated (region, bucket name, credentials, local file path, S3 object key).
2. A pre-flight check confirms the local file exists on the agent host. The task fails immediately if the file is not found — no AWS API call is made.
3. The extension authenticates to AWS using the provided credentials.
4. `PutObject` uploads the file to the specified key in the bucket.
5. The `uploaded_s3_uri` output field is updated in real time upon success.

**Completion behavior:** The task exits with code `0` on success. The `uploaded_s3_uri` field contains the full `s3://bucket/key` URI and is preserved on re-run.

---

## Task Configuration

### Authentication

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| AWS Credentials | UAC Credential entity. Username = Access Key ID; Password = Secret Access Key. | Yes | `aws-prod-credentials` |

### General

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| Action | The S3 operation to perform: `List Objects` or `Upload File`. Defaults to `List Objects`. | No | `Upload File` |
| AWS Region | AWS region where the target bucket resides. | Yes | `us-east-1` |
| Bucket Name | Name of the target S3 bucket. | Yes | `my-data-bucket` |

### Upload File (visible only when Action = Upload File)

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| Local File Path | Absolute path on the agent host for the file to upload. | Yes (when visible) | `/opt/reports/daily-report.csv` |
| S3 Object Key | Destination key (path) within the bucket. Must not start with `/`. | Yes (when visible) | `reports/2026/daily-report.csv` |

### Output Fields (read-only, populated by the extension)

| Field | Description | Visible When |
|-------|-------------|--------------|
| Object Count | Total number of objects found in the bucket. | Action = List Objects |
| Uploaded S3 URI | Full S3 URI of the successfully uploaded object. | Action = Upload File |

---

## Example Walkthroughs

### Scenario 1: List all objects in a bucket

**Goal:** Count and retrieve metadata for all objects in the `audit-logs` S3 bucket in `eu-west-1`.

**Prerequisites:**
- A UAC Credential named `aws-audit-creds` exists with a valid Access Key ID and Secret Access Key.
- The IAM user/role associated with those credentials has `s3:ListBucket` permission on `audit-logs`.
- The `audit-logs` bucket exists in `eu-west-1`.

**Configuration:**

| Field | Value | Notes |
|-------|-------|-------|
| Action | `List Objects` | Default value; no change needed |
| AWS Credentials | `aws-audit-creds` | Select from the credential picker |
| AWS Region | `eu-west-1` | Must match the bucket's region |
| Bucket Name | `audit-logs` | |

**What happens:**

- The extension pages through the entire `audit-logs` bucket, updating `Object Count` after each page.
- On completion, `Object Count` shows the total number of objects found.
- Up to 100 object records (key, size, last modified) are included in the structured output.
- The value is visible in the task list view and preserved if the task is re-run.

---

### Scenario 2: Upload a local file to S3

**Goal:** Upload a nightly report generated on the agent host to the `company-reports` bucket.

**Prerequisites:**
- A UAC Credential named `aws-upload-creds` exists with a valid Access Key ID and Secret Access Key.
- The IAM user/role has `s3:PutObject` permission on `company-reports`.
- The `company-reports` bucket exists in `us-east-1`.
- The file `/opt/jobs/output/nightly-report.csv` exists on the agent host at task execution time.

**Configuration:**

| Field | Value | Notes |
|-------|-------|-------|
| Action | `Upload File` | Reveals the Local File Path and S3 Object Key fields |
| AWS Credentials | `aws-upload-creds` | Select from the credential picker |
| AWS Region | `us-east-1` | Must match the bucket's region |
| Bucket Name | `company-reports` | |
| Local File Path | `/opt/jobs/output/nightly-report.csv` | Absolute path on the agent host |
| S3 Object Key | `reports/nightly/2026-09-17-report.csv` | Do not start with `/` |

**What happens:**

- The extension verifies the local file exists before making any AWS call; the task fails fast if it is missing.
- `PutObject` uploads the file to `s3://company-reports/reports/nightly/2026-09-17-report.csv`.
- `Uploaded S3 URI` is updated in real time: `s3://company-reports/reports/nightly/2026-09-17-report.csv`.
- The URI is preserved on re-run and can be referenced by downstream tasks.

---

## Troubleshooting

### Authentication failure (exit code 1)

**Symptom:** Task fails with a message referencing `InvalidClientTokenId`, `SignatureDoesNotMatch`, or `InvalidAccessKeyId`.

**Possible cause:** The Access Key ID or Secret Access Key stored in the UAC Credential entity is incorrect or has been rotated.

**Resolution:** Open the UAC Credential entity referenced in the **AWS Credentials** field and update both the Username (Access Key ID) and Password (Secret Access Key) to valid, active values.

---

### Permission denied (exit code 1)

**Symptom:** Task fails with a message referencing `AccessDenied` and includes the operation name and bucket name.

**Possible cause:** The IAM policy attached to the credentials does not grant the required permission (`s3:ListBucket` or `s3:PutObject`) on the specified bucket.

**Resolution:** Review the IAM policy for the AWS user or role. Add the missing permission for the exact bucket ARN (e.g., `arn:aws:s3:::my-bucket` and `arn:aws:s3:::my-bucket/*` for object-level operations).

---

### Bucket not found (exit code 1)

**Symptom:** Task fails with a message referencing `NoSuchBucket`.

**Possible cause:** The bucket name is misspelled, the bucket does not exist, or the bucket exists in a different region than the one specified.

**Resolution:** Verify that the **Bucket Name** field matches the exact bucket name in AWS, and that **AWS Region** matches the region where the bucket was created.

---

### Local file not found — Upload File (exit code 20)

**Symptom:** Task fails before any AWS call with a validation error stating the local file path does not exist.

**Possible cause:** The file has not been created yet, the path is wrong, or the agent is running on a different host than where the file was written.

**Resolution:** Confirm the file exists on the agent host at the exact path specified in **Local File Path**. Ensure any preceding workflow step that generates the file has completed successfully before this task runs.

---

### S3 Object Key starts with `/` (exit code 20)

**Symptom:** Task fails at input validation with a message about an invalid object key.

**Possible cause:** The **S3 Object Key** field value begins with a `/` character, which is not a valid S3 key prefix.

**Resolution:** Remove the leading `/` from the object key (e.g., change `/reports/file.csv` to `reports/file.csv`).

---

### Network / connection timeout (exit code 1)

**Symptom:** Task fails with a message referencing `EndpointResolutionError`, `ConnectTimeoutError`, or `ReadTimeoutError`.

**Possible cause:** The agent host cannot reach the AWS S3 endpoint. This may be a transient network issue, a firewall rule, or a misconfigured VPC endpoint.

**Resolution:** Verify that the agent host has outbound HTTPS access to `s3.<region>.amazonaws.com`. Check firewall rules, security group egress policies, and proxy settings. Retry the task — transient timeouts often resolve on a second attempt.

---

### Input validation errors (exit code 20)

**Symptom:** Task fails immediately with one or more validation errors listing blank or missing fields.

**Possible cause:** A required field (**AWS Region**, **Bucket Name**, **Local File Path**, or **S3 Object Key**) was left empty.

**Resolution:** Open the task configuration and supply a value for every field marked as required for the selected action. See the [Field Reference](#field-reference) table for required/optional status.

---

## Field Reference

| Name | Label | Type | Required | Description | Allowed Values |
|------|-------|------|----------|-------------|----------------|
| `action` | Action | Choice | No (default: `List Objects`) | S3 operation to perform. | `List Objects`, `Upload File` |
| `aws_credentials` | AWS Credentials | Credential | Yes | AWS credentials. Username = Access Key ID; Password = Secret Access Key. | Any valid UAC Credential entity |
| `aws_region` | AWS Region | Text | Yes | AWS region where the target S3 bucket resides. | Any valid AWS region identifier, e.g. `us-east-1`, `eu-west-1` |
| `bucket_name` | Bucket Name | Text | Yes | Name of the target S3 bucket. | Any valid S3 bucket name |
| `local_file` | Local File Path | Text | Yes (when Action = Upload File) | Absolute path on the agent host for the file to upload. Visible only when Action = `Upload File`. | Any valid absolute filesystem path |
| `s3_object_key` | S3 Object Key | Text | Yes (when Action = Upload File) | Destination object key within the bucket. Must not start with `/`. Visible only when Action = `Upload File`. | Any valid S3 object key (no leading `/`) |
| `object_count` | Object Count | Text (Output Only) | — | Total number of objects found in the bucket. Populated by the extension. Visible only when Action = `List Objects`. | Populated automatically |
| `uploaded_s3_uri` | Uploaded S3 URI | Text (Output Only) | — | Full S3 URI of the successfully uploaded object. Populated by the extension. Visible only when Action = `Upload File`. | Populated automatically (`s3://bucket/key`) |
