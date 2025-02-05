"""
Production settings for reckless project.
"""
import environ
from .base import *

# Initialize environ
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Security settings
SECURE_SSL_REDIRECT = False
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_CONTENT_TYPE_NOSNIFF = True
#X_FRAME_OPTIONS = 'DENY'
#SECURE_HSTS_SECONDS = 31536000
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

CSRF_TRUSTED_ORIGINS = [
    'https://recklessanalysis.com',
    'https://www.recklessanalysis.com',
]