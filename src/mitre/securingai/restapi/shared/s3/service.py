from typing import IO, Optional, Union
from urllib.parse import urlunparse

import structlog
from boto3.session import Session
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from injector import inject
from structlog.stdlib import BoundLogger
from werkzeug.datastructures import FileStorage

LOGGER: BoundLogger = structlog.stdlib.get_logger()


class S3Service(object):
    @inject
    def __init__(self, session: Session, client: BaseClient) -> None:
        self._session = session
        self._client = client

    def upload(
        self, fileobj: Union[IO[bytes], FileStorage], bucket: str, key: str, **kwargs
    ) -> Optional[str]:
        log: BoundLogger = kwargs.get("log", LOGGER.new())

        log.info("Uploading data to S3", fileobj=fileobj, bucket=bucket, key=key)

        try:
            self._client.upload_fileobj(Fileobj=fileobj, Bucket=bucket, Key=key)

        except ClientError:
            log.exception("S3 upload failed", fileobj=fileobj, bucket=bucket, key=key)
            return None

        uri: str = self.as_uri(bucket=bucket, key=key)
        log.info("S3 upload successful", uri=uri)

        return uri

    @staticmethod
    def as_uri(bucket: Optional[str], key: Optional[str], **kwargs) -> str:
        log: BoundLogger = kwargs.get("log", LOGGER.new())  # noqa: F841

        return urlunparse(("s3", bucket or "", key or "", "", "", ""))
