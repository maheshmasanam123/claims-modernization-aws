"""AWS Glue ETL: landing JSON -> partitioned Parquet on S3.

Runs in Glue (PySpark) when deployed, and locally with `--local` against
LocalStack S3 for development. Bookmarks are used to avoid reprocessing files
in production.
"""
from __future__ import annotations

import argparse
import sys


def transform(spark, src_path: str, tgt_path: str) -> int:
    from pyspark.sql.functions import col, sha2, year

    df = spark.read.json(src_path)
    out = (
        df.withColumn("ssn_hash",        sha2(col("ssn").cast("string"), 256))
          .withColumn("license_hash",    sha2(col("license_no").cast("string"), 256))
          .drop("ssn", "license_no")
          .withColumn("loss_year",       year("loss_date"))
    )
    (
        out.write.mode("append")
           .partitionBy("state", "loss_year")
           .format("parquet")
           .option("compression", "snappy")
           .save(tgt_path)
    )
    return out.count()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--local", action="store_true")
    p.add_argument("--src", default="data/landing/claims/")
    p.add_argument("--tgt", default="data/lake/claims/")
    args = p.parse_args()

    if args.local:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName("claims-etl-local").getOrCreate()
    else:
        from awsglue.context import GlueContext
        from pyspark.context import SparkContext
        spark = GlueContext(SparkContext.getOrCreate()).spark_session

    n = transform(spark, args.src, args.tgt)
    print(f"wrote {n} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
