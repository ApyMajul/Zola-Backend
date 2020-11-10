"""Django settings for Zola project: base module.

Every setting defined in this module will be propagated to all other settings
modules.
"""

import os
from datetime import timedelta
from pathlib import Path
from django.utils.translation import ugettext_lazy as _

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Used to construct absolute links outside of views
BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:3001"

# ALLMECEN_ENVIRONMENT = os.environ.get('AMCENV', 'default')

PARENT_DIR = Path(__file__).parent.parent.parent  # the repo root
SRC_DIR = PARENT_DIR
DIST_DIR = PARENT_DIR / 'dist'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't1k(t)h%x-lci1j+9p*d*f*^yy164fpbt-*ydu&z2@)b)jd7=_'


DEBUG = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'corsheaders',

    'django_extensions',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'taggit',
    'mptt',

    'accounts',
    'books',
    'comments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [SRC_DIR / 'templates'],
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

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [SRC_DIR / 'templates'],
#         'OPTIONS': {
#             'loaders': [
#                 'django.template.loaders.filesystem.Loader',
#                 'django.template.loaders.app_directories.Loader',
#             ],
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#                 'django.template.context_processors.media',
#             ],
#         },
#     },
# ]

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


ROOT_URLCONF = 'zola.urls'

WSGI_APPLICATION = 'zola.wsgi.application'

STATIC_URL = '/static/'
STATIC_ROOT = DIST_DIR / 'static_root'
STATICFILES_DIRS = [
    SRC_DIR / 'static',
]

# store static files locally and serve with whitenoise
STATICFILES_STORAGE = 'zola.settings.utils.WhiteNoiseStaticFilesStorage'

# ############ GRAPHENE ########################

GRAPHENE = {
    'SCHEMA': 'zola.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}


# ############ AUTH ########################
AUTH_USER_MODEL = 'accounts.User'

ACCOUNT_ACTIVATION_DAYS = 7

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

GRAPHQL_JWT = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LONG_RUNNING_REFRESH_TOKEN': True,
    'JWT_EXPIRATION_DELTA': timedelta(minutes=5),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}

# ############ i18n / l10n ########################

TIME_ZONE = 'Europe/Paris'

USE_L10N = True

USE_I18N = True

USE_TZ = True

LANGUAGE_CODE = 'en-us'

LANGUAGES = (
    ('en', _('English')),
    ('fr', _('French')),
)

DATE_INPUT_FORMATS = ['%d/%m/%Y']
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
TIME_FORMAT = '%H:%M:%S.%f'

# LOCALE_PATHS = (
#     str(PARENT_DIR / './i18n/locale'),
# )

# ############ Content ########################

# Maximum allowed size in bytes for user-submitted files
MAX_FILE_SIZES = {
    "avatar": 5*1024*1024,
    "video_thumbnail": 5*1024*1024,
    "audio_thumbnail": 5*1024*1024,
}
