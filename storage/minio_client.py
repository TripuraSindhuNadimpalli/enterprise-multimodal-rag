from io import BytesIO

from minio import Minio

from config.settings import settings


client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)


def ensure_bucket_exists() -> None:
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def upload_file(
    object_name: str,
    data: bytes,
    content_type: str,
) -> None:
    ensure_bucket_exists()

    client.put_object(
        bucket_name=settings.minio_bucket,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def download_file(object_name: str) -> bytes:
    response = client.get_object(
        bucket_name=settings.minio_bucket,
        object_name=object_name,
    )

    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()

def delete_file(object_name: str) -> None:
    client.remove_object(
        bucket_name=settings.minio_bucket,
        object_name=object_name,
    )