
from django.conf import settings

from storages.backends.s3boto import S3BotoStorage

class S3FileStorage(S3BotoStorage):
    """ File storage which prefixes the key with FILE_STORAGE_PREFIX  """
    location = getattr(settings, 'FILE_STORAGE_PREFIX', None)
    
