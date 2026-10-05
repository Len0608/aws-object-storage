# UAC Entities

**Extension:** aws-object-storage

---

## Agent Selection

### Available Agents

| Agent Name | Host | IP | Type | Status | Queue | Version |
|------------|------|----|------|--------|-------|---------|
| AGT_LINUX_PS5 | ip-30-0-1-83 | 30.0.1.83 | Linux/Unix | Offline | AGNT0071 | 7.7.1.1 |
| nginx-with-sidecar - AKS-SIDECAR-TEST | nginx-with-sidecar | 10.244.4.224 | Linux/Unix | Active | AKS-SIDECAR-TEST | 7.9.2.2 |
| sb-agent-ubu - AGNT0012 | sb-agent-ubu | 127.0.1.1 | Linux/Unix | Active | AGNT0012 | 7.9.0.0 |
| UDMG-SB | ip-172-31-2-26.us-east-2.compute.internal | 172.31.2.26 | Linux/Unix | Active | AGNT0118 | 7.9.2.0 |
| AGT_LINUX_PS1 | packaged-solutions-1 | 30.0.1.111 | Linux/Unix | Active | AGNT0009 | 8.0.0.0 |

### Selected Agent

| Field      | Value |
|------------|-------|
| Agent Name | nginx-with-sidecar - AKS-SIDECAR-TEST |
| Host Name  | nginx-with-sidecar |
| IP Address | 10.244.4.224 |
| Type       | Linux/Unix |
| Status     | Active |
| Queue Name | AKS-SIDECAR-TEST |
| Version    | 7.9.2.2 |
| SysID      | 2ed88652f231458ba5d81a4db5ef398c |

**Required OS Type:** Linux/Unix
**Selection rationale:** First Active Linux/Unix agent found in the controller's agent list. The extension is Linux-only (agentType: Linux/Unix) per template.json and analysis.md.

---

## Required Entities

[Populated by test-graph-builder based on planned test scenarios]

### Credentials

| Credential Name | Type | Field Name | Auth Method | Used In Scenarios |
|----------------|------|------------|-------------|-------------------|
| aws-s3-test-credentials | Local (Basic Auth) | aws_credentials | AWS Access Key (user = Access Key ID, password = Secret Access Key) | Test_AwsObjectStorage_ListObjects_Minimal, Test_AwsObjectStorage_ListObjects_MaxOutputRecords, Test_AwsObjectStorage_UploadFile_Minimal, Test_AwsObjectStorage_UploadFile_NestedPath, Test_AwsObjectStorage_UploadFile_RootKey, Test_AwsObjectStorage_ListObjects_LargeOutputCap |

### Scripts

_No script fields are defined in the extension template. No UAC Script entities are required._

---

## Created Entities

[Populated by main thread after creation on UAC]

### Credentials

| Credential Name | SysID | Status |
|----------------|-------|--------|
| | | |

### Scripts

| Script Name | SysID | Status |
|------------|-------|--------|
| | | |
