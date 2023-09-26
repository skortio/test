import os
import sys

DEBUG = True
BASE_PATH = os.path.dirname(__file__)


ALLOWED_HOSTS = ["127.0.0.1", "webpage.boledragon.com"]
SESSION_COOKIE_NAME = 'dragon-vegas-ses'
SESSION_COOKIE_AGE = 86400


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'admin_vegas',
        'USER': 'bole',
        'PASSWORD': 'kXg5TV3n1',
        'HOST': 'dragon-product-aurora01-cluster.cluster-cx0gmqabavlj.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {'charset':'utf8mb4'}, 
    },
    'product': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_vegas',
        'USER': 'bole',
        'PASSWORD': 'kXg5TV3n1',
        'HOST': 'dragon-product-aurora01-cluster.cluster-cx0gmqabavlj.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {'charset':'utf8mb4'}, 
    },
    'product_ro': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'product_vegas',
        'USER': 'bole',
        'PASSWORD': 'kXg5TV3n1',
        'HOST': 'dragon-product-aurora01-cluster.cluster-ro-cx0gmqabavlj.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {'charset':'utf8mb4'}, 
    },
    'vegas_ro': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vegas',
        'USER': 'bole',
        'PASSWORD': 'tyu567%^&',
        'HOST': 'dragon-unity-aurora01-cluster.cluster-ro-cx0gmqabavlj.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
    },
}

SECRET_KEY = 'django-insecure-zbz7kywo*z^z^fp@0^ygk3+bi983)$x7k39ir9ngbh)tlrv((#'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_PATH, 'templates')],
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


INSTALLED_APPS = [
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django_apscheduler",
    'django_ses',
    'sender'
]

ROOT_URLCONF = 'sender.urls'

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_PATH, 'static'),
    os.path.join(BASE_PATH, 'upload'),
]

MEDIA_ROOT = os.path.join(BASE_PATH, 'upload')

WSGI_APPLICATION = 'sender.wsgi.application'

EMAIL_BACKEND = 'django_ses.SESBackend'
#AWS_ACCESS_KEY_ID = ''
#AWS_SECRET_ACCESS_KEY = ''

AWS_SES_REGION_NAME = 'us-west-2'
AWS_SES_REGION_ENDPOINT = 'email.us-west-2.amazonaws.com'

# If you want to use the SESv2 client
USE_SES_V2 = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s][%(name)s] %(levelname)s %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'stderr': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
        },
        'stdout': {
            'level': 'INFO',
            'formatter': 'verbose',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/slots_forever/mail_sender.log',
            'formatter': 'simple',
            'when': 'MIDNIGHT',
            'backupCount': 7,
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AWS_SES_CONFIGURATION_SET = 'dragon-vegas-set'

try:
    from local_settings import *  # noqa: E262,F401,F403
except ImportError:
    pass

