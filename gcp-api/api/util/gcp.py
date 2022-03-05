import os

from google.cloud import storage


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str) -> None:
    """ファイルをGCSにアップロードする"""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)


def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str) -> None:
    """ファイルをGCSからダウンロードする"""

    # フォルダの作成
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
