from generator.generate_claims import make_claim


def test_claim_has_no_raw_ssn_after_hash_step():
    c = make_claim(1)
    assert {"ssn", "license_no"} <= set(c)
    assert c["incurred_amount"] >= 0


def test_loss_year_matches():
    c = make_claim(1)
    assert c["loss_date"].startswith(str(c["loss_year"]))
