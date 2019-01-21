"""
Django settings for the DOC Trips project.
"""

import os

import dj_database_url

from .loader import EnvLoader


BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))

# Untracked file used to store secrets for local development
DEV_CONFIG = os.path.join(BASE_DIR, '..', 'config.yml')

env = EnvLoader(DEV_CONFIG)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get('SECRET_KEY')

# Is this the development environment?
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.get('DEBUG', False)

# Are we testing on Travis?
TESTING = env.get('TRAVIS', False)

# Or is this a production environment?
PRODUCTION = not (DEBUG or TESTING)

# AWS SECRET KEYS and CONFIG
AWS_ACCESS_KEY_ID = env.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env.get('AWS_STORAGE_BUCKET_NAME')

GOOGLE_MAPS_KEY = env.get('GOOGLE_MAPS_KEY')
GOOGLE_MAPS_BROWSER_KEY = env.get('GOOGLE_MAPS_BROWSER_KEY')

# Don't overwrite identically named files
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
DEFAULT_FILE_STORAGE = 'fyt.utils.storages.S3FileStorage'
FILE_STORAGE_PREFIX = 'uploads'

# CanonicalHostMiddleware redirects requests for HEROKU_HOST to
# CANONICAL_HOST.
HEROKU_HOST = 'doc-trips.herokuapp.com'
CANONICAL_HOST = 'www.doctrips.org'

# Sentry monitoring
RAVEN_CONFIG = {'dsn': env.get('SENTRY_DSN')}

# For Heroku
ALLOWED_HOSTS = ['*']

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
    'fyt.applications',
    'fyt.core',
    'fyt.croos',
    'fyt.dartdm',
    'fyt.emails',
    'fyt.gear',
    'fyt.incoming',
    'fyt.permissions',
    'fyt.raids',
    'fyt.reports',
    'fyt.safety',
    'fyt.timetable',
    'fyt.training',
    'fyt.transport',
    'fyt.trips',
    'fyt.users',
    'fyt.utils',
    'fyt.webauth',
]
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar', 'test_without_migrations']
    INTERNAL_IPS = ['127.0.0.1']

MIDDLEWARE = (
    [
        'django.middleware.security.SecurityMiddleware',
        'fyt.middleware.CanonicalHostMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]
    + (['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG else [])
    + [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'fyt.webauth.middleware.WebAuthMiddleware',  # enable Dartmouth WebAuth
        'fyt.users.middleware.UserEmailRequiredMiddleware',  # fix email lookup failures
        'fyt.middleware.UserLoggerMiddleware',
    ]
)

AUTH_USER_MODEL = 'users.DartmouthUser'
AUTHENTICATION_BACKENDS = ('fyt.webauth.backends.WebAuthBackend',)
# Dartmouth WebAuth server
CAS_SERVER_URL = 'https://login.dartmouth.edu/cas/'

# login_required decorator redirects to here; this is the Webauth login.
LOGIN_URL = '/users/login/'

# Security/SSL settings
if PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

ROOT_URLCONF = 'fyt.urls'

WSGI_APPLICATION = 'fyt.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(env.get('DATABASE_URL'), conn_max_age=500)
}

# Forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'
CRISPY_FAIL_SILENTLY = PRODUCTION

# Increase the allowed number of POST parameters so that some large
# formsets don't cause issues
DATA_UPLOAD_MAX_NUMBER_FIELDS = 3000

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = False
USE_L10N = False
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATICFILES_STORAGE = 'fyt.utils.storages.WhitenoisePipelineStorage'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

# Pipeline - static files
PIPELINE = {
    # Concatenate assets only -- GzipManifest deals with compression
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
                'css/font-awesome-v4-shims.min.css',
                'css/summernote.css',
                'css/metisMenu.css',
            ),
            'output_filename': 'base.css',
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
                'js/timer.js',
            ),
            'output_filename': 'base.js',
        },
        'summernote': {
            'source_filenames': ('js/summernote.js', 'js/init_summernote.js'),
            'output_filename': 'my_summernote.js',
        },
    },
}


_TEMPLATE_LOADERS = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]
if not DEBUG:
    _TEMPLATE_LOADERS = [['django.template.loaders.cached.Loader', _TEMPLATE_LOADERS]]

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
        },
    }
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {'format': '%(levelname)s  %(message)s %(pathname)s:%(lineno)s'}
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
        'django': {'handlers': ['console', 'sentry'], 'level': 'INFO'},
        'fyt': {  # project namespace
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
        },
    },
}

DEBUG_TOOLBAR_CONFIG = {
    # Disable poor performance caused by the templates panel.
    # See https://github.com/jazzband/django-debug-toolbar/issues/910
    'DISABLE_PANELS': {
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
    },
    # Use local jQuery (for offline debugging)
    'JQUERY_URL': '',
}
