#!/usr/bin/env python3

# This script uploads the contents of a directory or a single file to an S3 bucket.
# The AWS credentials can be stored in the ~/.aws/credentials file or in environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or passed as arguments.
# The script uses the boto3 library to interact with the S3 service.
# The script can be run as follows:
# python push_s3.py <bucket_name> <source> [-d <destination>] [--aws_access_key_id <aws_access_key_id>] [--aws_secret_access_key <aws_secret_access_key>] [--endpoint_url <endpoint_url>]

import argparse
import os
import sys
import boto3
from botocore.client import Config

def get_file_from_s3(client, bucket_name, object_name, dest_path):
    """Try to download a single file from an S3 bucket."""
    try:
        client.download_file(bucket_name, object_name, dest_path)
        print(f"File '{object_name}' successfully downloaded from bucket '{bucket_name}' to '{dest_path}'.")
    except Exception as e:
        print(f"Error downloading file: {e}")
        if "AccessDenied" in str(e):
            print("Access denied. Please check your AWS credentials and permissions.")
            sys.exit(1)
        elif "NoSuchBucket" in str(e):
            print("Bucket does not exist. Please check the bucket name.")
            sys.exit(2)
        elif "NoSuchKey" in str(e):
            # This does not raise an error, just a warning
            print("Warning: Object does not exist. Please check the object name.")
        else:
            # Any other error
            sys.exit(3)

def upload_file_to_s3(client, bucket_name, file_path, object_name):
    """Upload a single file to an S3 bucket."""
    try:
        client.upload_file(file_path, bucket_name, object_name)
        print(f"File '{file_path}' successfully uploaded to bucket '{bucket_name}' as '{object_name}'.")
    except Exception as e:
        print(f"Error uploading file: {e}")
        if "AccessDenied" in str(e):
            print("Access denied. Please check your AWS credentials and permissions.")
            sys.exit(1)
        elif "NoSuchBucket" in str(e):
            print("Bucket does not exist. Please check the bucket name.")
            sys.exit(2)
        else:
            # Any other error
            sys.exit(3)

def upload_directory_to_s3(client, bucket_name, source, dest):
    """Upload the contents of a directory to an S3 bucket."""

    for root, dirs, files in os.walk(source):
        for file in files:
            file_path = os.path.join(root, file)
            if dest:
                dest_path = os.path.relpath(file_path, source)
                dest_path = os.path.join(dest, dest_path)
            else:
                dest_path = file_path
            upload_file_to_s3(client, bucket_name, file_path, dest_path)

def main():
    """Parse command-line arguments and upload a directory or single file to an S3 bucket.
       Store the AWS credentials in the ~/.aws/credentials file or in environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or pass them as arguments. 
    """

    parser = argparse.ArgumentParser(description="Upload the contents of a directory or a single file to a S3 bucket.")
    parser.add_argument("bucket_name", help="The name of the S3 bucket.")
    parser.add_argument("source", help="The path to the directory or file to upload.")
    parser.add_argument("-d", "--destination", help="Optional destination path.")
    parser.add_argument("-k", "--aws_access_key_id", help="AWS access key ID.")
    parser.add_argument("-s", "--aws_secret_access_key", help="AWS secret access key.")
    parser.add_argument("--endpoint_url", help="Custom endpoint URL for S3.", default="https://lumidata.eu")
    parser.add_argument("-g", "--get", action="store_true", help="Flag to download a single file from the S3 bucket instead of uploading. Destination is intended as a path on the remote.")

    args = parser.parse_args()

    config = Config(signature_version='s3')
    s3 = boto3.client('s3',
                      aws_access_key_id=args.aws_access_key_id,
                      aws_secret_access_key=args.aws_secret_access_key,
                      endpoint_url=args.endpoint_url,
                      config=config)

    if args.get:  # Download a single file from the S3 bucket
        if args.destination:
            dest_path = args.destination
        else:
            dest_path = os.path.basename(args.source)
        get_file_from_s3(s3, args.bucket_name, dest_path, args.source)  # source and destination are flipped in meaning
    else:
        if os.path.isdir(args.source):
            upload_directory_to_s3(s3, args.bucket_name, args.source, args.destination)
        else:
            if args.destination:
                dest_path = args.destination
            else:
                dest_path = os.path.basename(args.source)

            upload_file_to_s3(s3, args.bucket_name, args.source, dest_path)

if __name__ == "__main__":
    main()
