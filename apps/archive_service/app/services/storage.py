import json
from datetime import datetime, timezone
from io import BytesIO

import boto3
from botocore.exceptions import ClientError

from apps.archive_service.app.config import get_settings


class ArchiveStorage:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self.client = boto3.client(
            "s3",
            endpoint_url=f"{'https' if settings.minio_secure else 'http'}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name="us-east-1",
        )

    def ensure_bucket(self) -> None:
        bucket = self.settings.minio_bucket
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)

    def store_json(self, object_type: str, object_id: str, payload: dict) -> str:
        self.ensure_bucket()
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        key = f"{object_type}/{object_id}/{ts}.json"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.client.upload_fileobj(
            Fileobj=BytesIO(body),
            Bucket=self.settings.minio_bucket,
            Key=key,
            ExtraArgs={"ContentType": "application/json"},
        )
        return key


archive_storage = ArchiveStorage()
