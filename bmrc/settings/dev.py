from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2s09*r=51z9kzr&#7)b7agq($j4o_6!e!0x+g8q%#5&51-_0m@'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# MarkLogic settings (placeholder values for development)
# These are overridden in local.py for actual development/production use
MARKLOGIC_SERVER = ''
MARKLOGIC_USERNAME = ''
MARKLOGIC_PASSWORD = ''
PROXY_SERVER = ''

try:
    from .local import *
except ImportError:
    pass
