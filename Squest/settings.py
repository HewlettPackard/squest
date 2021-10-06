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
import time

from celery.schedules import crontab

from service_catalog.utils import str_to_bool, get_mysql_dump_major_version, \
    get_celery_crontab_parameters_from_crontab_line

# LOAD configuration from the environment
SECRET_KEY = os.environ.get('SECRET_KEY', 'sxuxahnezvrrea2vp97et=q(3xmg6nk4on92+-+#_s!ikurbh-')
DEBUG = str_to_bool(os.getenv('DEBUG', True))
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'squest_db')
MYSQL_USER = os.environ.get('MYSQL_USER', 'squest_user')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'squest_password')
MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
LDAP_ENABLED = str_to_bool(os.environ.get('LDAP_ENABLED', False))
BACKUP_ENABLED = str_to_bool(os.environ.get('BACKUP_ENABLED', False))
BACKUP_CRONTAB = os.environ.get('BACKUP_CRONTAB', "0 1 * * *")  # every day at 1 AM
DOC_IMAGES_CLEANUP_ENABLED = str_to_bool(os.environ.get('DOC_IMAGES_CLEANUP_ENABLED', False))
DOC_IMAGES_CLEANUP_CRONTAB = os.environ.get('DOC_IMAGES_CLEANUP', "30 1 * * *")  # every day at 1:30 AM.

# -------------------------------
# SQUEST CONFIG
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
TESTING = sys.argv[1:2] == ['test']
COLLECTING_STATIC = sys.argv[1:2] == ['collectstatic']
IS_GUNICORN_EXECUTION = False
if "gunicorn" in sys.argv[0]:
    IS_GUNICORN_EXECUTION = True

print(f"BASE_DIR: {BASE_DIR}")
print(f"DEBUG: {DEBUG}")
print(f"TESTING: {TESTING}")
print(f"COLLECTING_STATIC: {COLLECTING_STATIC}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"IS_GUNICORN_EXECUTION: {IS_GUNICORN_EXECUTION}")
print(f"LDAP_ENABLED: {LDAP_ENABLED}")
print(f"BACKUP_ENABLED: {BACKUP_ENABLED}")
if BACKUP_ENABLED:
    print(f"BACKUP_CRONTAB: {BACKUP_CRONTAB}")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
    'guardian',
    'tempus_dominus',
    'django_node_assets',
    'django_filters',
    'drf_yasg',
    'taggit',
    'martor',
    'django_tables2',
    'dbbackup',
    'service_catalog',
    'resource_tracker',
    'profiles',
    'django_cleanup.apps.CleanupConfig',  # should stay last to override delete method of our model
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
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
TEMPLATES_DIR = str(BASE_DIR) + os.sep + 'templates'
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
        'NAME': MYSQL_DATABASE,
        'USER': MYSQL_USER,
        'PASSWORD': MYSQL_PASSWORD,
        'HOST': MYSQL_HOST,
        'PORT': MYSQL_PORT,
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
if LDAP_ENABLED:
    from Squest.ldap_config import *

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

LANGUAGE_CODE = os.environ.get('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Paris')
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_REDIRECT_URL = 'service_catalog:home'
LOGOUT_REDIRECT_URL = 'service_catalog:home'

# -----------------------------------------
# Static files https://docs.djangoproject.com/en/3.1/howto/static-files/
# -----------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'project-static')  # project statics
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# -----------------------------------------
# NODE CONFIG https://github.com/whitespy/django-node-assets
# -----------------------------------------
STATICFILES_FINDERS = [
    'django_node_assets.finders.NodeModulesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
NODE_PACKAGE_JSON = os.path.join(BASE_DIR, 'package.json')
NODE_MODULES_ROOT = os.path.join(BASE_DIR, 'node_modules')

# -----------------------------------------
# LOGGING CONFIG
# -----------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # 'format': '{pathname}:{lineno} {levelname} {asctime} {module} {message}',
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
print(f"CELERY_BROKER_URL: {CELERY_BROKER_URL}")
# Add a five-minutes timeout to all Celery tasks.
CELERYD_TASK_SOFT_TIME_LIMIT = int(os.environ.get('CELERYD_TASK_SOFT_TIME_LIMIT', 300))
print(f"CELERYD_TASK_SOFT_TIME_LIMIT: {CELERYD_TASK_SOFT_TIME_LIMIT}")
CELERY_TASK_ALWAYS_EAGER = TESTING
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULER = 'service_catalog.celery_beat_scheduler.DatabaseSchedulerWithCleanup'
CELERY_BEAT_SCHEDULE = {}

# -----------------------------------------
# Squest email config
# -----------------------------------------
SQUEST_HOST = os.environ.get('SQUEST_HOST', "http://squest.domain.local")
SQUEST_EMAIL_HOST = os.environ.get('SQUEST_EMAIL_HOST', "squest.domain.local")
SQUEST_EMAIL_NOTIFICATION_ENABLED = str_to_bool(os.environ.get('SQUEST_EMAIL_NOTIFICATION_ENABLED', False))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)

# -----------------------------------------
# Martor CONFIG https://github.com/agusmakmun/django-markdown-editor
# -----------------------------------------
# Choices are: "semantic", "bootstrap"
MARTOR_THEME = 'bootstrap'

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    'emoji': 'true',  # to enable/disable emoji icons.
    'imgur': 'true',  # to enable/disable imgur/custom uploader.
    'mention': 'false',  # to enable/disable mention
    'jquery': 'true',  # to include/revoke jquery (require for admin default django)
    'living': 'false',  # to enable/disable live updates in preview
    'spellcheck': 'false',  # to enable/disable spellcheck in form textareas
    'hljs': 'true',  # to enable/disable hljs highlighting in preview
}

# To show the toolbar buttons
MARTOR_TOOLBAR_BUTTONS = [
    'bold', 'italic', 'horizontal', 'heading', 'pre-code',
    'blockquote', 'unordered-list', 'ordered-list',
    'link', 'image-link', 'image-upload', 'emoji',
    'direct-mention', 'toggle-maximize', 'help'
]

# To setup the martor editor with title label or not (default is False)
MARTOR_ENABLE_LABEL = False

# Markdownify
MARTOR_MARKDOWNIFY_FUNCTION = 'martor.utils.markdownify'  # default
MARTOR_MARKDOWNIFY_URL = '/martor/markdownify/'  # default

# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',

    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',  # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',  # to parse markdown mention
    'martor.extensions.emoji',  # to parse markdown emoji
    'martor.extensions.mdx_video',  # to parse embed/iframe video
    'martor.extensions.escape_html',  # to handle the XSS vulnerabilities
]

# Markdown Extensions Configs
MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}

# Markdown urls
MARTOR_UPLOAD_PATH = 'doc_images/uploads'
MARTOR_UPLOAD_URL = '/api/uploader/'  # change to local uploader

# Maximum Upload Image
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_IMAGE_UPLOAD_SIZE = 5242880  # 5MB

# Markdown Extensions
# MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://www.webfx.com/tools/emoji-cheat-sheet/graphics/emojis/'     # from webfx
MARTOR_MARKDOWN_BASE_EMOJI_URL = 'https://github.githubassets.com/images/icons/emoji/'  # default from github
MARTOR_MARKDOWN_BASE_MENTION_URL = 'https://python.web.id/author/'  # please change this to your domain

# If you need to use your own themed "bootstrap" or "semantic ui" dependency
# replace the values with the file in your static files dir
# MARTOR_ALTERNATIVE_JS_FILE_THEME = "semantic-themed/semantic.min.js"   # default None
# MARTOR_ALTERNATIVE_CSS_FILE_THEME = "semantic-themed/semantic.min.css" # default None
MARTOR_ALTERNATIVE_JQUERY_JS_FILE = "jquery/dist/jquery.min.js"  # default None

if DOC_IMAGES_CLEANUP_ENABLED:
    CELERY_BEAT_SCHEDULE["cleanup_martor"] = {
        "task": "service_catalog.tasks.task_cleanup_ghost_docs_images",
        "schedule": crontab(**get_celery_crontab_parameters_from_crontab_line(DOC_IMAGES_CLEANUP_CRONTAB)),
    }

# -----------------------------------------
# DJANGO REST FRAMEWORK CONFIG
# -----------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'Squest.api.authentication.TokenAuthentication',
    )
}

# -----------------------------------------
# DJANGO TABLES2 TEMPLATE
# -----------------------------------------
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

# -----------------------------------------
# django-dbbackup https://django-dbbackup.readthedocs.io/en/master/index.html
# -----------------------------------------
DBBACKUP_CLEANUP_KEEP = int(os.environ.get('DBBACKUP_CLEANUP_KEEP', 5))
DBBACKUP_CLEANUP_KEEP_MEDIA = int(os.environ.get('DBBACKUP_CLEANUP_KEEP', 5))
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'backup'}
mysqldump_major_version = get_mysql_dump_major_version()
print(f"mysqldump major version: {mysqldump_major_version}")
if mysqldump_major_version < 10:
    DBBACKUP_CONNECTORS = {
        'default': {
            'DUMP_SUFFIX': '--no-tablespaces --column-statistics=0',
        }
    }
if BACKUP_ENABLED:
    CELERY_BEAT_SCHEDULE["perform_backup"] = {
        "task": "service_catalog.tasks.perform_backup",
        "schedule": crontab(**get_celery_crontab_parameters_from_crontab_line(BACKUP_CRONTAB)),
    }

# -----------------------------------------
# DJANGO GUARDIAN
# -----------------------------------------
GUARDIAN_RAISE_403 = True
