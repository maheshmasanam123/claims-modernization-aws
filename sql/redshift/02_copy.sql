-- Load Parquet from S3 lake into Redshift staging.
COPY staging.claims
FROM 's3://lake/claims/'
IAM_ROLE 'arn:aws:iam::{{ACCOUNT_ID}}:role/RedshiftCopyRole'
FORMAT AS PARQUET;

-- Idempotent upsert into analytics.fact_claims
BEGIN;
DELETE FROM analytics.fact_claims
USING staging.claims s
WHERE analytics.fact_claims.claim_id = s.claim_id;

INSERT INTO analytics.fact_claims
SELECT * FROM staging.claims;
COMMIT;
