"""
Django settings for Squest project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from service_catalog.utils import str_to_bool

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'sxuxahnezvrrea2vp97et=q(3xmg6nk4on92+-+#_s!ikurbh-'
DEBUG = True
TESTING = sys.argv[1:2] == ['test']
COLLECTING_STATIC = sys.argv[1:2] == ['collectstatic']
ALLOWED_HOSTS = ['*']
print("DEBUG: {}".format(DEBUG))
print("TESTING: {}".format(TESTING))
print("COLLECTING_STATIC: {}".format(COLLECTING_STATIC))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'fontawesome-free',
    'django_celery_results',
    'django_celery_beat',
    'guardian',
    'django_node_assets',
    'django_filters',
    'drf_yasg',
    'service_catalog',
    'resource_tracker'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Squest.urls'

TEMPLATES_DIR = str(BASE_DIR) + os.sep + '../templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Squest.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'squest_db'),
        'USER': os.environ.get('MYSQL_USER', 'squest_user'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'squest_password'),
        'HOST': os.environ.get('MYSQL_SERVICE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('MYSQL_SERVICE_PORT', '3306'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# -----------------------------------------
# LDAP
# -----------------------------------------
LDAP_ENABLED = str_to_bool(os.environ.get('LDAP_ENABLED', False))
if LDAP_ENABLED:
    from ldap_config import *

# -----------------------------------------
# Authentication
# -----------------------------------------
# do not use LDAP auth when testing
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    'guardian.backends.ObjectPermissionBackend',
]
if LDAP_ENABLED and not TESTING:
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'guardian.backends.ObjectPermissionBackend',
        'django_auth_ldap.backend.LDAPBackend',
    )

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# -----------------------------------------
# Static files https://docs.djangoproject.com/en/3.1/howto/static-files/
# -----------------------------------------

STATIC_URL = '/static/'
if COLLECTING_STATIC:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, '../project-static')  # project statics
    ]
    STATIC_ROOT = os.path.join(BASE_DIR, '../static')
else:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, '../static'),  # retrieve from collect static command
        os.path.join(BASE_DIR, '../project-static')  # project statics
    ]
MEDIA_ROOT = os.path.join(BASE_DIR, '../media')
MEDIA_URL = '/media/'
# https://github.com/whitespy/django-node-assets
STATICFILES_FINDERS = [
    'django_node_assets.finders.NodeModulesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
NODE_PACKAGE_JSON = os.path.join(BASE_DIR, '../package.json')
NODE_MODULES_ROOT = os.path.join(BASE_DIR, '../node_modules')

# -----------------------------------------
# LOGGING CONFIG
# -----------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': "DEBUG",
        },
    },
}

# -----------------------------------------
# CELERY CONFIG
# -----------------------------------------
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://rabbitmq:rabbitmq@localhost:5672/squest')
# Add a five-minutes timeout to all Celery tasks.
CELERYD_TASK_SOFT_TIME_LIMIT = 300
CELERY_TASK_ALWAYS_EAGER = TESTING
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'

# -----------------------------------------
# Squest CONFIG
# -----------------------------------------
SQUEST_HOST = "host.domain.example"
SQUEST_EMAIL_NOTIFICATION_ENABLED = False
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = 25
