"""
Django settings for 地球村民监察互助联盟 project.
"""

import os
from pathlib import Path
from cryptography.fernet import Fernet
import json

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Load configuration
CONFIG_FILE = BASE_DIR.parent / 'config.json'
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

SECRET_KEY = config.get('secret_key', 'django-insecure-dev-key-change-in-production')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # Local apps
    'apps.accounts',
    'apps.voting',
    'apps.list',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database (SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR.parent / 'data.db',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# CSRF settings for API - disable for debug/testing
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
CSRF_COOKIE_SECURE = False

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# CORS settings (for desktop app API calls)
CORS_ALLOW_ALL_ORIGINS = True if DEBUG else False

# File upload settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'media'

# Encryption key - will be initialized after loading admin config
ENCRYPTION_KEY = os.environ.get('APP_ENCRYPTION_KEY')

# Admin account (pre-seeded)
ADMIN_ACCOUNT = {
    'username': config['admin_username'],
    'password_hash': None,  # Will be set later
}


def _init_encryption():
    """延迟初始化加密器"""
    if not ENCRYPTION_KEY:
        import secrets
        key = Fernet.generate_key().decode()
        print(f"Generated new encryption key: {key}")
        return key

    try:
        Fernet(ENCRYPTION_KEY.encode())  # Validate existing key
        return ENCRYPTION_KEY
    except Exception:
        print("Invalid encryption key, generating new one...")
        import secrets
        return Fernet.generate_key().decode()


def get_cipher():
    """获取 Fernet 加密器"""
    from config.settings import _init_encryption as init_key
    global CIPHER
    if not 'CIPHER' in globals():
        key = init_key()
        CIPHER = Fernet(key.encode())
    return CIPHER
