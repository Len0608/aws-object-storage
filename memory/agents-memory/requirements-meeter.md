# Requirements Meeter Output

## Zipsafe Decision
- **Result**: False
- **Reason**: Packages with data files — boto3 contains JSON service model files and RST examples; botocore contains cacert.pem and extensive JSON service data files

## CLI Tools
- None required. All S3 operations are performed via the boto3 Python SDK bundled with the extension.

## Python Dependencies
- boto3==1.43.108 — Has data files (JSON resource models under `boto3/data/`, RST examples under `boto3/examples/`)
- botocore==1.43.108 — Has data files (cacert.pem, JSON service data under `botocore/data/`, partitions.json)
- s3transfer==0.19.2 — Pure Python (no non-Python files found)
- tabulate==0.10.0 — Pure Python (no non-Python files found)

## Setup.py Changes
- VENDOR_FOLDER added: no (no CLI tools to vendor; setup.py already includes conditional vendor logic)
- data_files updated: no (setup.py already contains the correct zip_safe=False data_files block with conditional vendor support)
