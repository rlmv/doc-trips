"""
Django settings for doc_fyt project.

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
SECRET_KEY = 'bbirkd_p03a$-6p45zzv!x)yv1+yw56*kvd(yc3o#@#j^ah=-!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

# heroku settings
ALLOWED_HOSTS = ['*']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = (

    # must be before admin
#    'grappelli',
#    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third party
    'django_cas',
    'django_behave',

    # custom
    'db',
    'user',
    'leader',
    'trip',
    'permissions',
)


TEST_RUNNER = 'django_behave.runner.DjangoBehaveTestSuiteRunner'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # enable Dartmouth WebAuth
    'django_cas.middleware.CASMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # TODO: do we need this with CAS?
    'django_cas.backends.CASBackend',
)

# django_cas / Dartmouth WebAuth settings 
CAS_SERVER_URL = 'https://login.dartmouth.edu/cas/'
CAS_RESPONSE_CALLBACKS = [ 'user.cas.dartmouth_cas_callback' ]
CAS_LOGOUT_COMPLETELY = True

# login_required decorator redirects to here. This is a django_cas view.
LOGIN_URL = '/user/login'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3'),
}

import datetime
# Dynamic settings. django-constance https://github.com/comoga/django-constance
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'trips_year': (2014, 'year of current trips'),
    'migration_date':  (datetime.datetime.today(), 'date to migrate'),
}

# ordered this way for Grappelli
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

# added request for Grappelli
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
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
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        '': { # all other namespaces
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
