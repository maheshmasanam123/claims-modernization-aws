-- Column-level masking via views. Analysts query these; raw PII never leaves.
CREATE OR REPLACE VIEW analytics.v_claims_masked AS
SELECT
    claim_id,
    policy_number,
    CASE WHEN CURRENT_USER IN ('claims_ops','fraud_team')
         THEN first_name ELSE 'REDACTED' END AS first_name,
    CASE WHEN CURRENT_USER IN ('claims_ops','fraud_team')
         THEN last_name  ELSE 'REDACTED' END AS last_name,
    state,
    line_of_business,
    loss_date,
    reported_date,
    status,
    incurred_amount,
    paid_amount,
    adjuster_id,
    ssn_hash,
    license_hash,
    loss_year
FROM analytics.fact_claims;

GRANT SELECT ON analytics.v_claims_masked TO GROUP analysts;
REVOKE ALL    ON analytics.fact_claims    FROM GROUP analysts;
