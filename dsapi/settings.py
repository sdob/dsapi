"""
Django settings for dsapi project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import dj_database_url
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles', # we're not serving static files, right?
    'corsheaders', # CORS headers for Django
    'rest_framework', # REST API framework
    'rest_framework.authtoken', # Token-based authentication
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'divesites', # Divesite and Dive models
    'comments', # Comments on places
    'profiles', # rich User profiles
    'authviews', # social auth hookups
    'actstream', # Activity stream
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsPostCsrfMiddleware', # CORS replace HTTPS referer
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dsapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates/password_reset.html'),
            ],
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

WSGI_APPLICATION = 'dsapi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# Parse db configuration from $DATABASE_URL
DATABASES = {
        'default': dj_database_url.config()
}

# Enable persistent connections --- disabling for the moment
# DATABASES['default']['CONN_MAX_AGE'] = 500


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
            )
        }

AUTHENTICATION_BACKENDS = (
        # Log in through Django admin
        'django.contrib.auth.backends.ModelBackend',
        # allauth-specific auth methods
        'allauth.account.auth_backends.AuthenticationBackend',
        )

# CORS stuff
# XXX: for development only!
CORS_ORIGIN_ALLOW_ALL = True
CORS_REPLACE_HTTPS_REFERER = True

CORS_ORIGIN_WHITELIST = (
        'facebook.com',
        'google.com',
        'dsfe.herokuapp.com',
        )

# Google reverse-geocoding url template string
GOOGLE_REVERSE_GEOCODING_URL_STRING_TEMPLATE = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s'

SITE_ID = 1

# django-allauth stuff
# Relax social account email verification configuration
# see: https://github.com/Tivix/django-rest-auth/issues/23
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_USERNAME_REQUIRED = False # could be the issue

# Social authentication callback URLs
FACEBOOK_AUTH_CALLBACK_URL = os.environ.get('FACEBOOK_AUTH_CALLBACK_URL') or 'http://localhost:9000/'
GOOGLE_AUTH_CALLBACK_URL = os.environ.get('GOOGLE_AUTH_CALLBACK_URL') or 'http://localhost:9000/'

SPARKPOST_API_KEY = os.environ.get('SPARKPOST_API_KEY')
EMAIL_BACKEND = 'sparkpost.django.email_backend.SparkPostEmailBackend'
