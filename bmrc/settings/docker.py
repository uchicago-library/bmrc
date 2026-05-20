import os

from .dev import *  # noqa: F401 F403

# Pull in any developer customizations if a local.py is bind-mounted in
try:
    from .local import *  # noqa: F401,F403
except ImportError:
    pass

# Docker-specific database configuration (overrides local.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'bmrc_dev'),
        'USER': os.environ.get('POSTGRES_USER', 'bmrc'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

DEBUG = True
