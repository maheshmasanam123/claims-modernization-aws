"""S3 PutObject -> start Glue job. Wired via EventBridge in Terraform."""
import os

import boto3


GLUE_JOB = os.environ.get("GLUE_JOB_NAME", "claims_etl_job")
glue = boto3.client("glue")


def handler(event, _ctx):
    rec = event["Records"][0]["s3"]
    src = f"s3://{rec['bucket']['name']}/{rec['object']['key']}"
    resp = glue.start_job_run(JobName=GLUE_JOB, Arguments={"--SRC_PATH": src})
    return {"job_run_id": resp["JobRunId"], "src": src}
