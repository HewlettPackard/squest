# Production settings
from Squest.settings.development import *
import os
# update default secret key if provided
from_env_secret_key = os.environ.get('SECRET_KEY', None)
if from_env_secret_key is not None:
    SECRET_KEY = from_env_secret_key
DEBUG = False
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../project-static/')  # project statics
]
STATIC_ROOT = os.path.join(BASE_DIR, '../static')
