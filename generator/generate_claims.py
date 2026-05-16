"""Generate synthetic insurance claims (CMS-style fields)."""
from __future__ import annotations

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker


fake = Faker()
Faker.seed(7)
random.seed(7)

LINES_OF_BUSINESS = ["AUTO", "HOME", "LIFE", "HEALTH"]
CLAIM_STATUSES = ["OPEN", "INVESTIGATING", "APPROVED", "DENIED", "PAID", "CLOSED"]
STATES = ["GA", "TX", "IL", "FL", "CA", "NY", "OH", "PA", "NC", "MI"]


def make_claim(i: int) -> dict:
    loss_date = fake.date_between(start_date="-3y", end_date="today")
    reported = loss_date + timedelta(days=random.randint(0, 30))
    return {
        "claim_id":       f"CLM-{i:09d}",
        "policy_number":  f"POL-{random.randint(10**8, 10**9 - 1)}",
        "ssn":            fake.ssn(),
        "license_no":     fake.bothify("?########").upper(),
        "first_name":     fake.first_name(),
        "last_name":      fake.last_name(),
        "state":          random.choice(STATES),
        "line_of_business": random.choice(LINES_OF_BUSINESS),
        "loss_date":      loss_date.isoformat(),
        "reported_date":  reported.isoformat(),
        "status":         random.choice(CLAIM_STATUSES),
        "incurred_amount": round(random.uniform(100, 250_000), 2),
        "paid_amount":     round(random.uniform(0, 200_000), 2),
        "adjuster_id":     f"ADJ-{random.randint(1000, 9999)}",
        "loss_year":       loss_date.year,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=10_000)
    p.add_argument("--out", default="data/landing/claims")
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    fname = out / f"claims_{date.today():%Y%m%d}.json"
    with fname.open("w", encoding="utf-8") as f:
        for i in range(args.rows):
            f.write(json.dumps(make_claim(i)) + "\n")
    print(f"wrote {args.rows} rows -> {fname}")


if __name__ == "__main__":
    main()
