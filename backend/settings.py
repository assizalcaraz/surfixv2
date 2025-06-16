from pathlib import Path
from decouple import config, Csv
import os


AUTH_USER_MODEL = 'login.CustomUser'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config("DJANGO_SECRET_KEY", default="insegura-en-dev")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    'https://ofi.surfix.store',
    'https://www.surfix.store',
    'https://surfix.store',
]


# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Uncomment this only if you have custom static folders outside apps
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', 
    'login',
    'listas',
    'cmr',
    'cobranza',
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config("POSTGRES_DB"),
        'USER': config("POSTGRES_USER"),
        'PASSWORD': config("POSTGRES_PASSWORD"),
        'HOST': config("POSTGRES_HOST", default='db'),
        'PORT': config("POSTGRES_PORT", default='5432'),
    }
}


WSGI_APPLICATION = 'backend.wsgi.application'
