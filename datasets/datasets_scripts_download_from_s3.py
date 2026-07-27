"""
Small helper to download files from S3 to local dataset dir.
Requires boto3 installed and AWS credentials available in env.
Usage:
python datasets/scripts/download_from_s3.py --bucket my-bucket --prefix "datasets/myset/" --out datasets/data/
"""
import argparse
import os
import boto3
import logging

logger = logging.getLogger("datasets.scripts")
logging.basicConfig(level=logging.INFO)


def download_prefix(bucket: str, prefix: str, out_dir: str):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    os.makedirs(out_dir, exist_ok=True)
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith("/"):
                continue
            dest = os.path.join(out_dir, os.path.basename(key))
            logger.info("Downloading s3://%s/%s -> %s", bucket, key, dest)
            s3.download_file(bucket, key, dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    download_prefix(args.bucket, args.prefix, args.out)


if __name__ == "__main__":
    main()