# Insurance Claims Modernization on AWS

Reference pipeline for an on-prem Hadoop → AWS modernization of insurance
claims data. Synthetic claims arrive in S3, are processed by AWS Glue (PySpark)
into Parquet on a partitioned S3 data lake, and loaded into Redshift for
actuarial reporting. PII columns are tagged in the Glue Catalog and masked at
the Redshift view layer.

## Architecture

```
       +------------------+
       | claims generator | -- writes JSON to s3://landing/claims/
       +------------------+
                |
                v
        +-----------------+        +--------------------+
        | AWS Glue job    | -----> | s3://lake/claims/  |
        | (PySpark)       |        |  parquet/snappy    |
        +-----------------+        |  partitioned by    |
                |                  |  state, loss_year  |
                |                  +--------------------+
                v                            |
        Glue Catalog (PII tags)              v
                |               +-------------------------+
                v               |  COPY into Redshift     |
        Athena ad-hoc           |  staging.claims         |
                                +-------------------------+
                                           |
                                           v
                                +------------------------+
                                |  masked Redshift views |
                                |  for analysts          |
                                +------------------------+
```

## Stack

- Synthetic data: Python + Faker (CMS-style claims fields)
- Storage: S3 (LocalStack for local runs)
- Compute: AWS Glue PySpark jobs (runnable locally via `glue-libs`)
- Catalog: AWS Glue Data Catalog with column-level PII tags
- Warehouse: Redshift Serverless (with masking views)
- IaC: Terraform modules for the whole stack
- Orchestration: EventBridge → Lambda trigger included

## Quick start (zero infrastructure)

```bash
pip install faker pandas pyarrow
python generator/generate_claims.py --rows 5000
python demo.py
```

Expected output: partitioned Parquet under `data/lake/claims/state=GA/loss_year=2025/...`, a masked analytics view under `data/gold/`, and a summary showing first_name = "REDACTED" and a 64-char SSN hash.

## AWS-flavored run (LocalStack or real AWS)

```bash
docker compose -f iac/docker-compose.localstack.yml up -d
python generator/generate_claims.py --rows 50000
python glue_jobs/claims_etl_job.py --local
```

## What this demonstrates

- Hadoop-to-AWS modernization pattern (Parquet on S3 + Redshift)
- AWS Glue PySpark ETL with bookmarks for incremental loads
- Glue Catalog table creation + PII column tagging
- Redshift COPY with manifest files
- Column-level masking via Redshift views (SSN, policy_number, license_no)
- Row-count reconciliation script (source vs Redshift)
- Terraform for full reproducibility

## Repo layout

```
generator/         Faker-based synthetic claims generator
glue_jobs/         PySpark Glue jobs (claims_etl, policy_dim_scd2)
sql/redshift/      DDL, COPY commands, masking views
iac/terraform/     S3, Glue, Redshift Serverless, IAM
lambda/            S3 PutObject -> Glue job trigger
tests/             unit tests for transformations
docs/              data dictionary, masking policy doc
```
