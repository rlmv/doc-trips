
from django.conf import settings
from pipeline.storage import PipelineMixin
from storages.backends.s3boto import S3BotoStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class S3FileStorage(S3BotoStorage):
    """
    File storage which prefixes the key with FILE_STORAGE_PREFIX
    """
    location = getattr(settings, 'FILE_STORAGE_PREFIX', None)


class WhitenoisePipelineStorage(PipelineMixin,
                                CompressedManifestStaticFilesStorage):
    """
    Use both Whitenoise and Pipeline for staticfiles
    """
