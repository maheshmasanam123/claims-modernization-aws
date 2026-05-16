CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.claims (
    claim_id         VARCHAR(20)    NOT NULL,
    policy_number    VARCHAR(20)    NOT NULL,
    first_name       VARCHAR(80),
    last_name        VARCHAR(80),
    state            CHAR(2),
    line_of_business VARCHAR(20),
    loss_date        DATE,
    reported_date    DATE,
    status           VARCHAR(20),
    incurred_amount  NUMERIC(14,2),
    paid_amount      NUMERIC(14,2),
    adjuster_id      VARCHAR(20),
    ssn_hash         CHAR(64),
    license_hash     CHAR(64),
    loss_year        INTEGER
)
DISTSTYLE KEY DISTKEY (claim_id)
COMPOUND SORTKEY (loss_date, state);
