terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.region
}

variable "region"   { default = "us-east-1" }
variable "project"  { default = "claims-modernization" }

resource "aws_s3_bucket" "landing" { bucket = "${var.project}-landing" }
resource "aws_s3_bucket" "lake"    { bucket = "${var.project}-lake" }

resource "aws_glue_catalog_database" "claims_db" { name = "claims_db" }

resource "aws_glue_catalog_table" "claims" {
  database_name = aws_glue_catalog_database.claims_db.name
  name          = "claims"
  table_type    = "EXTERNAL_TABLE"
  parameters    = { classification = "parquet", "has_encrypted_data" = "false" }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.lake.bucket}/claims/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    ser_de_info { serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe" }

    columns { name = "claim_id"        type = "string" }
    columns { name = "policy_number"   type = "string" parameters = { "PII" = "true" } }
    columns { name = "ssn_hash"        type = "string" parameters = { "PII" = "hashed" } }
    columns { name = "license_hash"    type = "string" parameters = { "PII" = "hashed" } }
    columns { name = "incurred_amount" type = "decimal(14,2)" }
    columns { name = "paid_amount"     type = "decimal(14,2)" }
  }

  partition_keys { name = "state"     type = "string" }
  partition_keys { name = "loss_year" type = "int" }
}

resource "aws_redshiftserverless_namespace" "ns" {
  namespace_name      = "${var.project}-ns"
  admin_username      = "admin"
  admin_user_password = "REPLACE_ME"
}

resource "aws_redshiftserverless_workgroup" "wg" {
  namespace_name = aws_redshiftserverless_namespace.ns.namespace_name
  workgroup_name = "${var.project}-wg"
  base_capacity  = 8
}
