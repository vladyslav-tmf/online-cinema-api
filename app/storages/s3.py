from typing import Union

import boto3
from botocore.exceptions import (
    BotoCoreError,
    NoCredentialsError,
    HTTPClientError,
    ConnectionError,
)

from app.exceptions.storage import S3ConnectionError, S3FileUploadError
from app.storages.interfaces import S3StorageInterface


class S3StorageClient(S3StorageInterface):
    def __init__(
        self, endpoint_url: str, access_key: str, secret_key: str, bucket_name: str
    ):
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket_name = bucket_name

        self._s3_client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        )

    def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> None:
        try:
            self._s3_client.put_object(
                Bucket=self._bucket_name,
                Key=file_name,
                Body=file_data,
                ContentType="application/octet-stream",
            )
        except (ConnectionError, HTTPClientError, NoCredentialsError) as e:
            raise S3ConnectionError(f"Failed to connect to S3 storage: {str(e)}") from e
        except BotoCoreError as e:
            raise S3FileUploadError(f"Failed to upload to S3 storage: {str(e)}") from e

    def get_file_url(self, file_name: str) -> str:
        return f"{self._endpoint_url}/{self._bucket_name}/{file_name}"
