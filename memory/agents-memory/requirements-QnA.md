# Requirements Completeness Assessment

The requirements are **High Detail**. The core intent is unambiguous: a Stonebranch Universal Extension named "AWS Object Storage" with two actions — List Objects and Upload File — powered by the `boto3` SDK, targeting an MVP/demo scope. Key decisions (action names, fields per action, SDK choice, and simplicity mandate) are all clearly stated.

A small number of decisions remain open: specifically how AWS credentials map to UAC Credential attributes, how output is structured for each action (STDOUT, Extension Output JSON, and UAC output-only fields), and whether a safety net is applied for large S3 bucket listings. The questions below shape those decisions precisely so the implementation phase can proceed without ambiguity.

---

# Platform Compatibility

**Platform Compatibility from Requirements**: Linux (confirmed — environment.md specifies OS: Linux, Architecture: x86_64)

**Platform Compatibility Agreement**: Linux-only (manylinux_2_17_x86_64)

---

# Python Modules and Versions

## Researched Modules

**boto3**
- **Module Purpose**: AWS SDK for Python — provides the high-level S3 client used for all S3 operations (list objects, upload file)
- **Version**: 1.43.108
- **Type**: Pure Python

**botocore**
- **Module Purpose**: Low-level AWS service client library — core dependency of boto3 that handles request signing, retries, and protocol handling
- **Version**: 1.43.108
- **Type**: Pure Python

**s3transfer**
- **Module Purpose**: Managed multipart S3 transfer library — core dependency of boto3 that handles efficient file uploads and downloads
- **Version**: 0.19.2
- **Type**: Pure Python

**tabulate**
- **Module Purpose**: Formats data as clean ASCII tables for STDOUT output — recommended by architect notes with `rounded_outline` style for readable object listings
- **Version**: 0.10.0
- **Type**: Pure Python

## Agreed Python Modules and Versions

| Module | Purpose | Version | Type |
|---|---|---|---|
| *Placeholder — to be updated after Q&A answers are applied* | | | |

---

# Question Rationale

The requirements define scope, actions, SDK, and core fields with precision. The open decisions cluster around three areas:

1. **Credential attribute mapping** — UAC Credential fields expose multiple attributes (`user`, `password`, `token`); the extension must use exactly one attribute per value with no fallback logic (per UAC policy). The AWS access key pair maps naturally to `user`/`password`, but this needs explicit confirmation.
2. **Output design** — the requirements say nothing about STDOUT format, Extension Output JSON structure, or which UAC output-only fields to populate. These choices directly affect the user experience and downstream automation usability.
3. **Large listing safety** — List Objects on a bucket with thousands of keys can produce output that bloats the UAC database. A record cap via `UE_MAX_OUTPUT_RECORDS` is the standard mitigation; whether to apply it here is a scope decision.

Answering these five questions fully specifies the extension for implementation.

---

# Clarifying Questions for Requirements Refinement

## Authentication & Security

**Question 1**: How should AWS credentials be mapped to UAC Credential field attributes?

- **Question Type**: Clarification on existing requirement
- **Context & Resources**: The requirements specify an "AWS Credentials" field, which maps to a UAC Credential Field. UAC Credential fields provide four attributes: `user`, `password`, `token`, and `passphrase`. UAC policy requires each credential value to map to exactly one attribute with no fallback logic. For AWS S3 with access-key authentication, the natural mapping is:
  - **Access Key ID** (non-secret identifier) → `user` attribute
  - **Secret Access Key** (secret) → `password` attribute

  In boto3, these are passed as `aws_access_key_id` and `aws_secret_access_key` when constructing the S3 client. This is the standard mapping pattern used across all AWS-based Universal Extensions.

  Further reading: [boto3 credentials configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

- **Question Dependencies**: None — this question is independent.
- **Recommended Answer**: Option A — Access Key ID → `user`, Secret Access Key → `password`.
- **Rationale**: This is the only mapping that satisfies the UAC Credential policy (no fallback logic, `user` always populated, sensitive value in `password`) while covering everything boto3 needs for S3 authentication.
- **Trade-offs**: Optimizes for policy compliance and simplicity. No alternatives are viable for standard access-key auth; IAM role-based auth (no credentials at all) would require changes to the field design and is out of scope for this MVP.
- **Requirement Impact**: No changes needed — confirms the implied design.
- **User's Answer**: Option A — Access Key ID → `user`, Secret Access Key → `password`.

---

## Essential Input/Output

**Question 2**: What should STDOUT display for the **List Objects** action?

- **Question Type**: New Discussion topic
- **Context & Resources**: STDOUT is the human-readable output shown in the UAC task instance view during and after execution. For a list of S3 objects, two options exist:

  - **Option A (Recommended)** — ASCII table with columns: `Object Key`, `Size (bytes)`, `Last Modified`. Rendered using the `tabulate` library (`rounded_outline` format). Example:

    ```
    ╭──────────────────────────┬────────────┬──────────────────────────╮
    │ Object Key               │ Size (bytes)│ Last Modified            │
    ├──────────────────────────┼────────────┼──────────────────────────┤
    │ data/report-2026.csv     │     142,308 │ 2026-09-15 10:22:43 UTC  │
    │ logs/app-2026-10-01.log  │   1,048,576 │ 2026-10-01 00:01:05 UTC  │
    ╰──────────────────────────┴────────────┴──────────────────────────╯
    ```

  - **Option B** — Plain text list of object keys only, one per line. Minimal output, easiest to implement.

  `tabulate` is a pure-Python module (v0.10.0, confirmed compatible) already planned as a dependency.

- **Question Dependencies**: None.
- **Recommended Answer**: Option A — ASCII table with Key, Size, Last Modified.
- **Rationale**: A table with size and date provides meaningful context at no extra implementation cost, and matches the architect notes' recommendation for tabular data on STDOUT.
- **Trade-offs**: Option A adds the `tabulate` dependency; Option B avoids it. For an MVP, the added clarity of a table outweighs the marginal dependency cost.
- **Requirement Impact**: Confirms inclusion of `tabulate==0.10.0` in `requirements.txt`.
- **User's Answer**: Option A — ASCII table with Object Key, Size (bytes), Last Modified.

---

**Question 3**: Should the **List Objects** action apply a record cap to prevent large bucket listings from bloating UAC storage?

- **Question Type**: New Discussion topic
- **Context & Resources**: S3 buckets can contain millions of objects. Writing all of them to STDOUT and Extension Output would bloat the UAC database and potentially exceed the Universal Agent output buffer. The standard mitigation is the **Large Output Safety Net Pattern**: an environment variable `UE_MAX_OUTPUT_RECORDS` caps how many records are written inline. The default is 100. When truncation occurs, a note in STDOUT and a warning in STDERR indicate the total count and applied limit.

  This cap applies only to inline output (STDOUT and Extension Output JSON); it has no effect on the actual S3 listing operation.

  - **Option A (Recommended)** — Apply `UE_MAX_OUTPUT_RECORDS` with default 100. When truncated, print a note: `"Showing 100 of 4,832 objects. Set UE_MAX_OUTPUT_RECORDS to display more."` Include `total_count` in Extension Output JSON regardless of the cap.
  - **Option B** — No cap; list all objects. Simpler code path but risky for any bucket with more than a few hundred objects.

- **Question Dependencies**: None.
- **Recommended Answer**: Option A — apply `UE_MAX_OUTPUT_RECORDS` with default 100.
- **Rationale**: Even for an MVP demo, a bucket used in testing might have hundreds of objects. Applying the safety net costs very little code and prevents a hard-to-debug failure at demo time.
- **Trade-offs**: Option A adds a few lines of environment variable handling; Option B is marginally simpler but can silently produce massive output.
- **Requirement Impact**: None — this is an operational safety feature, not a new functional requirement.
- **User's Answer**: Option A — apply `UE_MAX_OUTPUT_RECORDS` cap (default 100).

---

**Question 4**: What **output-only fields** should appear in the UAC task instance panel for each action?

- **Question Type**: New Discussion topic
- **Context & Resources**: UAC output-only fields are short values that appear directly in the task instance list view and detail panel without opening the full log. Architect notes recommend 2–3 fields maximum. Options per action:

  **For List Objects:**
  - **Option A (Recommended)** — Single field: `Object Count` (integer — number of objects found in the bucket).
  - **Option B** — No output-only fields; results visible only via STDOUT and Extension Output.

  **For Upload File:**
  - **Option A (Recommended)** — Single field: `S3 URI` (text — the full `s3://bucket-name/object-key` URI of the uploaded file).
  - **Option B** — No output-only fields; confirmation visible only via STDOUT.

  Both Option A choices together use two output-only fields, staying within the recommended 2–3 limit.

- **Question Dependencies**: None.
- **Recommended Answer**: Both Option A — Object Count for List Objects, S3 URI for Upload File.
- **Rationale**: These two fields give operators instant, actionable feedback (how many objects exist; where exactly the file landed) without requiring them to open the log. They are the most valuable single facts for each action.
- **Trade-offs**: Optimizes for operator UX at the cost of two additional output field definitions. No measurable downside for an MVP.
- **Requirement Impact**: Adds two output-only fields to the template definition: `object_count` (Integer Field) and `s3_uri` (Text Field).
- **User's Answer**: Option A for both actions — Object Count for List Objects, S3 URI for Upload File.

---

**Question 5**: What should the **Extension Output JSON** contain for each action?

- **Question Type**: New Discussion topic
- **Context & Resources**: Extension Output is the machine-processable JSON payload available when a task instance reaches a terminal state (Success or Failure). It is used by downstream tasks and automation workflows. For this extension, two structures are possible:

  **For List Objects:**
  - **Option A (Recommended)** — Include the full object listing (up to `UE_MAX_OUTPUT_RECORDS` items) plus total count:
    ```json
    {
      "result": {
        "bucket": "my-bucket",
        "total_count": 4832,
        "displayed_count": 100,
        "objects": [
          {"key": "data/report.csv", "size": 142308, "last_modified": "2026-09-15T10:22:43Z"},
          ...
        ]
      }
    }
    ```
  - **Option B** — Minimal: only the count and bucket name, no object list.

  **For Upload File:**
  - **Option A (Recommended)** — Confirmation with S3 URI and file size:
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
  - **Option B** — Minimal: only bucket and key, no size.

- **Question Dependencies**: Depends on Q3. If Q3=Option B (no cap), Option A for List Objects returns the full object list.
- **Recommended Answer**: Option A for both actions.
- **Rationale**: The richer structure makes the Extension Output useful for downstream workflow tasks (e.g., a follow-up task that processes each listed object). Adding size to the Upload confirmation makes it easy to verify the upload was complete. The cost is negligible.
- **Trade-offs**: Option A produces slightly more JSON; Option B is marginally simpler. For an MVP demo, Option A demonstrates the extension's automation value better.
- **Requirement Impact**: None — this is the implementation design for Extension Output, which is not constrained by the requirements.
- **User's Answer**: Option A for both actions — full object list with total count for List Objects; bucket, key, S3 URI, and size for Upload File.
