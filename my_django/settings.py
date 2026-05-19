"""
Django settings for my_django project.
"""

from pathlib import Path
from my_django.env_config import EnvConfig
from datetime import timedelta

#==========================================================
# Celery Beat Schedule
#==========================================================
from .configs.celery_schedules import CELERY_BEAT_SCHEDULE



# =========================================
# Default User Model
# =========================================
AUTH_USER_MODEL = 'authentication.User'

# =========================================
# load CONFIG
# =========================================
CONFIG = EnvConfig()


# =========================================
# Security
# =========================================
# Basic
SECRET_KEY = CONFIG.SECRET_KEY
DEBUG = CONFIG.DEBUG
ALLOWED_HOSTS = CONFIG.ALLOWED_HOSTS if not DEBUG else ['*']


# =========
# CORS
# =========
CORS_ALLOW_CREDENTIALS = CONFIG.CORS_ALLOW_CREDENTIALS
CORS_ALLOW_ALL_ORIGINS  = CONFIG.CORS_ALLOW_ALL_ORIGINS
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = CONFIG.CORS_ALLOWED_ORIGINS
    CORS_ALLOWED_ORIGIN_REGEXES = CONFIG.CORS_ALLOWED_ORIGIN_REGEXES
CSRF_TRUSTED_ORIGINS = CONFIG.CSRF_TRUSTED_ORIGINS
CORS_ALLOWED_METHODS = CONFIG.CORS_ALLOWED_METHODS
# CORS_ALLOW_HEADERS = config('CORS_ALLOWED_ORIGINS', default='', cast=str).split(",")
# if not CORS_ALLOW_HEADERS:
#     CORS_ALLOW_HEADERS = [
#         "authorization",
#         "content-type",
#     ]


# =========================================
# Base Config
# =========================================
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'my_django.urls'
WSGI_APPLICATION = 'my_django.wsgi.application'


# =========================================
# Internationalization
# =========================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================================
# Static files (CSS, JavaScript, Images)
# =========================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================
# Application definition
# =========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",

    # Self Define
    'authentication',
    'core',
    'emails',
    'otp',
    'my_test',
    'logs',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'logs.middleware.LoggingContextMiddleware',
]


# =========================================
# Django Rest Framework
# =========================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],

    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/min",
        "user": "200/min",
        "login": f"{CONFIG.LOGIN_THROTTLE_RATE_PER_MINUTE}/min",
        "register": f"{CONFIG.REGISTER_THROTTLE_RATE_PER_MINUTE}/min",
        "change_password": f"{CONFIG.CHANGE_PASSWORD_THROTTLE_RATE_PER_MINUTE}/min",
        "get_otp": f"{CONFIG.GET_OTP_THROTTLE_RATE_PER_DAY}/day",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "core.utils.exception_handler.custom_exception_handler",
}



# =========================================
# Template
# =========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# =========================================
# Database
# =========================================
DB_ENGINE = CONFIG.DB_ENGINE
if (DB_ENGINE == 'django.db.backends.sqlite3'):
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_ENGINE,
            'NAME': CONFIG.DB_NAME,
            'USER': CONFIG.DB_USER,
            'PASSWORD': CONFIG.DB_PASSWORD,
            'HOST': CONFIG.DB_HOST,
            'PORT': CONFIG.DB_PORT,
        }
    }


# =========================================
# Password validation
# =========================================
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


# =========================================
# Redis
# =========================================
REDIS_URL = CONFIG.REDIS_URL


# =========================================
# Cache
# =========================================
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }


# =========================================
# Celery
# =========================================
CELERY_BROKER_URL = CONFIG.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = CONFIG.CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_IGNORE_RESULT = True


# =========================================
# Email
# =========================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = CONFIG.EMAIL_HOST
EMAIL_PORT = CONFIG.EMAIL_PORT
EMAIL_HOST_USER = CONFIG.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = CONFIG.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = CONFIG.EMAIL_USE_TLS


# =========================================
# Simple JWT
# =========================================
SIMPLE_JWT = {
    # Basic
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "AUTH_HEADER_TYPES": ("Bearer",),
    # Lifetime
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=CONFIG.ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=CONFIG.REFRESH_TOKEN_LIFETIME_HOURS),
    # Properties
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    # Security
    "SIGNING_KEY": SECRET_KEY,
    "ALGORITHM": "HS256",
}


from logs.logging_config import get_logging_config
LOGGING = get_logging_config(service_name="my_backend")


