import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("LUCYNA_API_S3_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("LUCYNA_API_S3_SECRET_ACCESS_KEY"),
    endpoint_url=os.getenv("S3_ENDPOINT_URL"),
    config=Config(signature_version="s3v4"),
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def upload_file(file: UploadFile, filename="NULL"):
    # Use default filename if no filename specified
    if filename == "NULL":
        filename = file.filename
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, filename)
        return {"message": f"File {filename} uploaded successfully."}
    except ClientError as e:
        return {"error": str(e)}


def download_file(file_name: str):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
        return response["Body"].read()
    except ClientError as e:
        return {"error": str(e)}


def delete_file(file_name: str):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        return {"message": f"File {file_name} deleted successfully."}
    except ClientError as e:
        return {"error": str(e)}


def get_presigned_url(file_name: str, expiration=3600):
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_name},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        print(e)
        return None
