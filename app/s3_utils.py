import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
import os
from dotenv import load_dotenv

load_dotenv()

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("LUCYNA_API_S3_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("LUCYNA_API_S3_SECRET_ACCESS_KEY"),
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


async def upload_file(file: UploadFile):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, file.filename)
        return {"message": f"File {file.filename} uploaded successfully."}
    except ClientError as e:
        return {"error": str(e)}


def download_file(file_name: str):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
        return response["Body"].read()
    except ClientError as e:
        return {"error": str(e)}
