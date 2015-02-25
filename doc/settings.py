"""
Django settings for doc-trips project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# AWS SECRET KEYS and CONFIG
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

# don't overwrite identically named files
# TODO: change this if we move static files to S3!
# - will need to implement custom storage classes for STATIC and MEDIA
AWS_S3_FILE_OVERWRITE = False
DEFAULT_FILE_STORAGE = 'doc.utils.storages.S3FileStorage'
FILE_STORAGE_PREFIX = 'uploads'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)
TEMPLATE_DEBUG = DEBUG

# monitoring
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', ''),
}

# Don't need this because we're using Raven/Sentry
# ADMINS = (('Bo', 'bo.marchman@gmail.com'),)
# MANAGERS = ADMINS

# SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'root@localhost')
# EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER', '')
# EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT', '')
# EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN', None)
# EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD', None)

# heroku settings
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'crispy_forms',
    'bootstrap3_datetime',
    'django_extensions',
    'raven.contrib.django.raven_compat',

    # site apps
    'doc.db',
    'doc.users',
    'doc.dartdm', 
    'doc.applications',
#    'leaders',
    'doc.croos', 
    'doc.transport',
    'doc.trips',
    'doc.permissions',
    'doc.timetable',
    'doc.webauth', 
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # enable Dartmouth WebAuth
    'doc.webauth.middleware.WebAuthMiddleware',
)

AUTH_USER_MODEL = 'users.DartmouthUser'
AUTHENTICATION_BACKENDS = (
    'doc.webauth.backends.WebAuthBackend',
)
# Dartmouth WebAuth settings. TODO: move this to cas app?
CAS_SERVER_URL = 'https://login.dartmouth.edu/cas/'
CAS_LOGOUT_COMPLETELY = True

# login_required decorator redirects to here. This is webauth login.
LOGIN_URL = '/users/login'

ROOT_URLCONF = 'doc.urls'

WSGI_APPLICATION = 'doc.wsgi.application'

# used for local testing instead of Postgres
import dj_database_url
sqlite = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(default=sqlite)
}
# Enable Connection Pooling on Heroku databases
# see https://devcenter.heroku.com/articles/python-concurrency-and-database-connections
#if not DATABASES['default']['NAME'] == 'db.sqlite3':
#DATABASES['default']['ENGINE'] = 'django_postgrespool'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
# from https://devcenter.heroku.com/articles/django-app-configuration
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s  %(message)s %(pathname)s:%(lineno)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        '': { # all other namespaces
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
