from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = ['*']

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(BASE_DIR, "cache")
    }
}

try:
    from .local import *
except ImportError:
    pass
