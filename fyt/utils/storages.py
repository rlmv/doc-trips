from django.conf import settings
from pipeline.storage import PipelineMixin
from storages.backends.s3boto3 import S3Boto3Storage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class S3FileStorage(S3Boto3Storage):
    """
    File storage which prefixes the key with FILE_STORAGE_PREFIX
    """

    location = getattr(settings, 'FILE_STORAGE_PREFIX', None)


class WhitenoisePipelineStorage(PipelineMixin, CompressedManifestStaticFilesStorage):
    """
    Use both Whitenoise and Pipeline for staticfiles
    """
