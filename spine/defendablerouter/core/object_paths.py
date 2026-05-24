from __future__ import annotations

from defendablerouter.schemas.router_receipt import ObjectStorage

DEFAULT_BUCKET = "streetledger"


def build_object_storage(
    client_id: str,
    app_id: str,
    assignment_id: str,
    bucket: str = DEFAULT_BUCKET,
) -> ObjectStorage:
    prefix = f"router/{client_id}/{app_id}/{assignment_id}/"
    uri = f"s3://{bucket}/{prefix}"
    return ObjectStorage(bucket=bucket, prefix=prefix, uri=uri)
