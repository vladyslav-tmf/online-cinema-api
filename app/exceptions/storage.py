class BaseS3Error(Exception):
    def __init__(self, message=None):
        if not message:
            message = "An S3 storage error occurred."
        super().__init__(message)


class S3ConnectionError(BaseS3Error):
    def __init__(self, message="Failed to connect to S3 storage."):
        super().__init__(message)


class S3BucketNotFoundError(BaseS3Error):
    def __init__(self, message="S3 bucket not found."):
        super().__init__(message)


class S3FileUploadError(BaseS3Error):
    def __init__(self, message="Failed to upload file to S3."):
        super().__init__(message)


class S3FileNotFoundError(BaseS3Error):
    def __init__(self, message="Requested file not found in S3."):
        super().__init__(message)


class S3PermissionError(BaseS3Error):
    def __init__(self, message="Insufficient permissions to access S3 resource."):
        super().__init__(message)
