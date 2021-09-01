import os

_environment = os.getenv('SQUEST_ENV', 'development')
print(f"SQUEST_ENV: {_environment}")
if _environment == "production":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Squest.settings.production")
    from Squest.settings.production import *
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Squest.settings.development")
    from Squest.settings.development import *

__version__ = "0.2b"
VERSION = __version__


print(f"DEBUG: {DEBUG}")
print(f"TESTING: {TESTING}")
print(f"COLLECTING_STATIC: {COLLECTING_STATIC}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
