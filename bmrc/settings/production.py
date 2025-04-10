from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "cache"
    }
}

try:
    from .local import *
except ImportError:
    pass
