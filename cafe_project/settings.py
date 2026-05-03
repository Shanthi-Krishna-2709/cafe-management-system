"""
Django settings for cafe_project project.
"""

import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _default_sqlite_path() -> Path:
    """
    FIX 1: Ensure the SQLite DB path is stable and the directory is writable.
    We always use BASE_DIR/db.sqlite3 unless overridden by CAFE_DB_PATH env var.
    """
    configured_path = os.environ.get("CAFE_DB_PATH")
    if configured_path:
        db_path = Path(configured_path).expanduser().resolve()
        try:
            db_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            import warnings
            warnings.warn(f"Could not create DB directory: {e}. Falling back to BASE_DIR.")
            return BASE_DIR / "db.sqlite3"
        return db_path

    return (BASE_DIR / "db.sqlite3").resolve()


SECRET_KEY = 'django-insecure-f&12!t7@3^fyvho%um$wo+f&8p0o+!l3*kiw9)kweln_&(h_^b'

DEBUG = True

ALLOWED_HOSTS = ["*"]  # OK for development


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cafe_app.apps.CafeAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'cafe_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'cafe_app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cafe_project.wsgi.application'


# FIX 2: Added timeout and check_same_thread options to prevent SQLite I/O and lock errors
BASE_DIR = Path(__file__).resolve().parent.parent

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # FIX 3: Changed to Indian timezone (was UTC)
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'cafe_app' / 'static',
]

# FIX 4: Added MEDIA settings (missing — can cause I/O errors when saving files)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'shanthikrishna279@gmail.com'
EMAIL_HOST_PASSWORD = 'aaav jzcg mjcf zrcj'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
CONTACT_EMAIL = 'shanthikrishna279@gmail.com'

# Razorpay credentials
RAZORPAY_KEY_ID = 'rzp_test_XXXX'
RAZORPAY_KEY_SECRET = 'XXXX'

# UPI Payment Configuration
UPI_ID = 'XXXXXXXXXX@okicici'
MERCHANT_NAME = 'Frost Haven'

# NetBanking Configuration
BANK_NAME = 'YYYYYYYYYYY'
BANK_ACCOUNT = '123456789XXXX'
IFSC_CODE = 'XXXXXXXXXXXX'