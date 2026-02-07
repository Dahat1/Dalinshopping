"""
Django settings for core project.
Updated for Dictionary Based Multi-Language System
"""

from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g%t@5!lr-y9a-r&+uufsk%7d%73l@hb4q&io!-0%bilki3ffs@'

# --- PRODUCTION AYARLARI ---
DEBUG = True

# Sitenin çalışacağı adresler
ALLOWED_HOSTS = [
    'www.dalinshopping.com',
    'dalinshopping.com',
    'webapp-2943067.pythonanywhere.com', # Senin PythonAnywhere ID'n
    'localhost',
    '127.0.0.1'
]

# HTTPS üzerinden Form gönderebilmek için gerekli
CSRF_TRUSTED_ORIGINS = [
    'https://www.dalinshopping.com',
    'https://dalinshopping.com',
]

# PythonAnywhere için Proxy Ayarı
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # Dil tespiti için gerekli (Kalsın)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'store' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # --- YENİ EKLENEN KISIM ---
                # Senin oluşturduğun context_processors.py dosyasını buraya bağlıyoruz.
                # Artık her sayfada {{ t.kelime }} çalışacak.
                'store.context_processors.language_processor', 
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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


# --- DİL AYARLARI (BASİTLEŞTİRİLDİ) ---
# Artık karmaşık dosya yollarına gerek yok.
# Sadece temel ayarlar ve dil listesi yeterli.

LANGUAGE_CODE = 'en-us' 

TIME_ZONE = 'Asia/Baghdad'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Desteklenen Diller (Navbar'daki set_language fonksiyonu için gerekli)
LANGUAGES = [
    ('en', _('English')),
    ('ar', _('Arabic')),
    ('ckb', _('Kurdish')), # ku yerine ckb yaptık
]


# --- STATIC & MEDIA FILES ---

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Giriş/Çıkış Yönlendirmeleri
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# --- EMAIL AYARLARI ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'Dalin Shopping <noreply@dalinshopping.com>'