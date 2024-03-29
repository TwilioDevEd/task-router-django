"""
Common Django settings for the project.

See the local, test, and production settings modules for the values used
in each environment.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""
import os

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_PATH = Path(BASE_DIR).parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'not-so-secret'

ALLOWED_HOSTS = ['*']

# Automatically load .env file
dotenv_path = PROJECT_PATH / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Twilio API credentials
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

HOST = os.environ.get('HOST')
BOB_NUMBER = os.environ.get('BOB_NUMBER')
ALICE_NUMBER = os.environ.get('ALICE_NUMBER')

# E-mail address that will receive transcriptions from voicemail
MISSED_CALLS_EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'your@email.here')

if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN):
    missing_config_values = """
    You must set the TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
    environment variables to run this app.
    Consult the README for instructions on how to find them.
    """
    raise ImproperlyConfigured(missing_config_values)

# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
)

THIRD_PARTY_APPS = (
)

LOCAL_APPS = (
    'task_router',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'task_router.middleware.AppendSlashWithoutRedirect',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

APPEND_SLASH = True

ROOT_URLCONF = 'twilio_sample_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
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

WSGI_APPLICATION = 'twilio_sample_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = BASE_DIR + '/staticfiles'

STATIC_URL = '/static/'

# Messages settings for Bootstrap 3

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Redirect login to /support/dashboard
LOGIN_REDIRECT_URL = '/support/dashbaord'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
