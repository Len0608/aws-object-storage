🌐 EXTERNAL SERVICE SETUP: Amazon S3

BEFORE RUNNING TESTS, CREATE THE FOLLOWING ON THE EXTERNAL SERVICE:

1. AWS IAM User with Access Keys
   - What: An IAM user (or existing user) with programmatic access credentials (Access Key ID + Secret Access Key)
   - Why: The extension authenticates to AWS using these credentials stored in a UAC Credential field. Without valid credentials, all actions fail with AuthenticationError.
   - How:
     1. Sign in to the AWS Management Console → IAM → Users → Create user
     2. Select "Programmatic access" (or attach access keys to an existing user)
     3. Under "Permissions", attach the inline or managed policy covering the permissions in step 2 below
     4. After creation, download or copy the Access Key ID and Secret Access Key — these are shown only once
   - Example: Access Key ID: `AKIAIOSFODNN7EXAMPLE`, Secret Access Key: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

2. IAM Policy with S3 Permissions
   - What: A policy granting `s3:ListBucket` and `s3:PutObject` on the test bucket
   - Why: The List Objects action requires `s3:ListBucket`; the Upload File action requires `s3:PutObject`. Missing either permission causes an AuthenticationError at runtime.
   - How:
     1. In IAM, create a policy with the following JSON (replace `<bucket-name>` with your test bucket name):
        ```json
        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": ["s3:ListBucket"],
              "Resource": "arn:aws:s3:::<bucket-name>"
            },
            {
              "Effect": "Allow",
              "Action": ["s3:PutObject"],
              "Resource": "arn:aws:s3:::<bucket-name>/*"
            }
          ]
        }
        ```
     2. Attach this policy to the IAM user created in step 1
   - Example: Policy name `ue-test-s3-policy` attached to user `ue-test-user`

3. S3 Bucket in a Known Region
   - What: An existing S3 bucket in a specific AWS region
   - Why: Both actions (List Objects and Upload File) require a pre-existing bucket specified via the `bucket_name` field. The extension does not create buckets.
   - How:
     1. Go to the AWS Management Console → S3 → Create bucket
     2. Choose a globally unique bucket name (lowercase, no spaces)
     3. Select the AWS region that matches what you will enter in the `aws_region` task field
     4. Leave all other defaults (block public access enabled is fine)
     5. Click "Create bucket"
   - Example: Bucket name `ue-test-bucket-20261005`, region `us-east-1`

---

🖥️ AGENT HOST SETUP

BEFORE RUNNING TESTS, PREPARE THE FOLLOWING ON THE UAC AGENT MACHINE:

1. Test Input File for Upload File Action
   - What: A local file at a known absolute path on the UAC Agent host, used as the upload source in Upload File test cases
   - Why: The `local_file` field must point to a file that exists and is readable on the agent filesystem at task execution time. If the file is absent, the task exits with LocalFileNotFoundError before any S3 call is made.
   - How: SSH into the agent host and run:
     ```bash
     mkdir -p ~/ue-test-input
     echo "key,value\ntest,data\n2026-10-05,run1" > ~/ue-test-input/test-upload.csv
     ```
   - Example: File path `~/ue-test-input/test-upload.csv` with content:
     ```
     key,value
     test,data
     2026-10-05,run1
     ```

---

📋 CHECKLIST:

  ☐ AWS IAM user created with programmatic access (Access Key ID + Secret Access Key noted)
  ☐ IAM policy granting s3:ListBucket and s3:PutObject attached to the IAM user
  ☐ S3 test bucket created in a known region (bucket name and region noted)
  ☐ Test input file created on agent host at ~/ue-test-input/test-upload.csv
  ☐ Verified: AWS credentials can authenticate (e.g. `aws s3 ls s3://<bucket-name>` succeeds from the agent host or local machine)
  ☐ Verified: Test file exists on agent host (`ls ~/ue-test-input/test-upload.csv`)
