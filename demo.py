"""End-to-end demo using pandas instead of PySpark.

Runs the same logical pipeline (landing JSON -> partitioned Parquet -> masked
analytics view) so reviewers can see real output without Spark / AWS.

Usage:
    python generator/generate_claims.py --rows 5000
    python demo.py
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


LANDING = Path("data/landing/claims")
LAKE    = Path("data/lake/claims")
GOLD    = Path("data/gold/claims")


def _hash(s: str) -> str:
    return hashlib.sha256(str(s).encode()).hexdigest()


def bronze_to_silver() -> pd.DataFrame:
    files = sorted(LANDING.glob("claims_*.json"))
    if not files:
        raise SystemExit("no landing files. run: python generator/generate_claims.py")
    df = pd.concat([pd.read_json(f, lines=True) for f in files], ignore_index=True)

    df["ssn_hash"]     = df["ssn"].map(_hash)
    df["license_hash"] = df["license_no"].map(_hash)
    df = df.drop(columns=["ssn", "license_no"])
    df["loss_date"]     = pd.to_datetime(df["loss_date"])
    df["reported_date"] = pd.to_datetime(df["reported_date"])
    df["loss_year"]     = df["loss_date"].dt.year

    LAKE.mkdir(parents=True, exist_ok=True)
    for (state, year), grp in df.groupby(["state", "loss_year"]):
        out = LAKE / f"state={state}/loss_year={year}"
        out.mkdir(parents=True, exist_ok=True)
        grp.to_parquet(out / "part.parquet", index=False)
    print(f"silver: wrote {len(df)} rows partitioned by state, loss_year")
    return df


def masked_analytics_view(df: pd.DataFrame, role: str = "analyst") -> pd.DataFrame:
    """Mirror the Redshift masking view logic in pandas."""
    masked = df.copy()
    if role != "claims_ops" and role != "fraud_team":
        masked["first_name"] = "REDACTED"
        masked["last_name"]  = "REDACTED"
    GOLD.mkdir(parents=True, exist_ok=True)
    out = GOLD / f"v_claims_masked_{role}.parquet"
    masked.to_parquet(out, index=False)
    print(f"gold: wrote masked view for role={role} -> {out}")
    return masked


def main() -> None:
    df = bronze_to_silver()
    masked = masked_analytics_view(df, role="analyst")

    print("\n=== analytics view summary ===")
    print(f"rows:           {len(masked):,}")
    print(f"unique policies: {masked['policy_number'].nunique():,}")
    print(f"states:         {masked['state'].nunique()}")
    print(f"incurred total: ${masked['incurred_amount'].sum():,.2f}")
    print(f"paid total:     ${masked['paid_amount'].sum():,.2f}")
    print("\nclaim status mix:")
    print(masked["status"].value_counts().to_string())
    print("\nPII check (first_name should be REDACTED for analyst role):")
    print(masked[["claim_id", "first_name", "last_name", "ssn_hash"]].head(3).to_string(index=False))


if __name__ == "__main__":
    main()
