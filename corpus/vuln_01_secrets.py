"""Planted flaws: hardcoded secrets. Expected: secret-aws, secret-token, secret-assignment."""
import boto3

AWS_ACCESS_KEY_ID = "AKIAEXAMPLEEXAMPLE12"
GITHUB_TOKEN = "ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
password = "S3cretPassword!"

def connect():
    return boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY_ID)
