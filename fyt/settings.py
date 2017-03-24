"""
Django settings for doc-trips project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

import dj_database_url
from model_mommy.generators import gen_string


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# AWS SECRET KEYS and CONFIG
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')

GOOGLE_MAPS_KEY = os.environ.get('GOOGLE_MAPS_KEY', '')
GOOGLE_MAPS_BROWSER_KEY = os.environ.get('GOOGLE_MAPS_BROWSER_KEY', '')

# don't overwrite identically named files
# TODO: change this if we move static files to S3!
# - will need to implement custom storage classes for STATIC and MEDIA
AWS_S3_FILE_OVERWRITE = False
DEFAULT_FILE_STORAGE = 'fyt.utils.storages.S3FileStorage'
FILE_STORAGE_PREFIX = 'uploads'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

# monitoring
RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', ''),
}

# heroku settings
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap3_datetime',
    'crispy_forms',
    'django_extensions',
    'django_tables2',
    'pipeline',
    'raven.contrib.django.raven_compat',
    'test_without_migrations',

    'fyt.applications',
    'fyt.croos',
    'fyt.dartdm',
    'fyt.db',
    'fyt.emails',
    'fyt.incoming',
    'fyt.permissions',
    'fyt.raids',
    'fyt.reports',
    'fyt.safety',
    'fyt.timetable',
    'fyt.transport',
    'fyt.trips',
    'fyt.users',
    'fyt.utils',
    'fyt.webauth',
]
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fyt.webauth.middleware.WebAuthMiddleware',  # enable Dartmouth WebAuth
    'fyt.users.middleware.UserEmailRequiredMiddleware',  # fix email lookup failures
]

AUTH_USER_MODEL = 'users.DartmouthUser'
AUTHENTICATION_BACKENDS = (
    'fyt.webauth.backends.WebAuthBackend',
)
# Dartmouth WebAuth settings. TODO: move this to cas app?
CAS_SERVER_URL = 'https://login.dartmouth.edu/cas/'
CAS_LOGOUT_COMPLETELY = True

# login_required decorator redirects to here. This is webauth login.
LOGIN_URL = '/users/login/'

# Security/SSL settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

ROOT_URLCONF = 'fyt.urls'

WSGI_APPLICATION = 'fyt.wsgi.application'

# Fallback on SQLite for local testing instead of Postgres
# sqlite = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': dj_database_url.config(conn_max_age=500)
#    'default': dj_database_url.config(default=sqlite, conn_max_age=500)
}
# TODO: use PgBouncer for connection pooling?
# https://devcenter.heroku.com/articles/python-concurrency-and-database-connection

# Forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = not DEBUG

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATICFILES_STORAGE = 'fyt.utils.storages.WhitenoisePipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

# Pipeline - static files
PIPELINE = {
    # concatenate assets only -- GzipManifest deals with compression
    'CSS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'JS_COMPRESSOR': 'pipeline.compressors.NoopCompressor',
    'STYLESHEETS': {
        'base': {
            'source_filenames': (
                'css/style.css',
                'css/typeaheadjs.css',
                'css/bootstrap.min.css',
                'css/bootstrap-theme.min.css',
                'css/font-awesome.min.css',
                'css/bootstrap-switch.css',
                'css/summernote.css',
                'css/metisMenu.css',
            ),
            'output_filename': 'base.css'
        }
    },
    'JAVASCRIPT': {
        'base': {
            'source_filenames': (
                'js/jquery.js',
                'js/bootstrap.min.js',
                'js/typeahead.bundle.js',
                'dartdm/lookup.js',  # must come after typeahead
                'js/stupidtable.js',
                'js/metisMenu.min.js',
                'js/bootstrap-switch.js',
            ),
            'output_filename': 'base.js'
        },
        'summernote': {
            'source_filenames': (
                'js/summernote.js',
                'js/init_summernote.js',
            ),
            'output_filename': 'my_summernote.js'
        }
    }
}


_TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
]
if not DEBUG:
    _TEMPLATE_LOADERS = [
        ['django.template.loaders.cached.Loader', _TEMPLATE_LOADERS],
    ]

_TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.media',
    'django.template.context_processors.request',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'loaders': _TEMPLATE_LOADERS,
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS,
        }
    }
]

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
        'sentry': {
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',
        },
        'fyt': {  # project namespace
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
        },
    },
}

# model-mommy testing
MOMMY_CUSTOM_FIELDS_GEN = {
    'fyt.users.models.NetIdField': gen_string,
}

# django-filters: Remove "Filter" and "Exclude" help text
FILTERS_HELP_TEXT_EXCLUDE = False
FILTERS_HELP_TEXT_FILTER = False
