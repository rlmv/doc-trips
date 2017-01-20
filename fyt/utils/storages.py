
from django.conf import settings
from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
from whitenoise.django import GzipManifestStaticFilesStorage


class S3FileStorage(S3BotoStorage):
    """
    File storage which prefixes the key with FILE_STORAGE_PREFIX
    """
    location = getattr(settings, 'FILE_STORAGE_PREFIX', None)


class GzipManifestPipelineStorage(PipelineMixin, GzipManifestStaticFilesStorage):
    """
    Use both Gzip and Pipeline for staticfiles
    """
    pass

