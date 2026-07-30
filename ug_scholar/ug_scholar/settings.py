import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local configuration before reading any settings. The project-root file
# is preferred, while the package-level location is supported for existing
# installations. Values supplied by the host environment always take priority.
load_dotenv(BASE_DIR / ".env", override=False)
load_dotenv(BASE_DIR / "ug_scholar" / ".env", override=False)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}

# Generating a new key on every process start invalidates signed sessions and
# makes authentication intermittent across workers. Development gets a stable
# local-only key; production must provide a real secret.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            "ug-scholar-local-development-key-change-before-production-"
            "7e3d2cb4e1b64b86a23f"
        )
    else:
        raise ImproperlyConfigured(
            "DJANGO_SECRET_KEY must be configured when DJANGO_DEBUG is false."
        )
SECRET_KEY_FALLBACKS = [
    key.strip()
    for key in os.getenv("DJANGO_SECRET_KEY_FALLBACKS", "").split(",")
    if key.strip()
]

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # 3rd party apps
    "corsheaders",
    'rest_framework',
    
    # internal apps
    'accounts.apps.AccountsConfig',
    'dashboard.apps.DashboardConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
     "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ug_scholar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/templates'],
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

WSGI_APPLICATION = 'ug_scholar.wsgi.application'
ASGI_APPLICATION = 'ug_scholar.asgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if os.getenv("DATABASE_URL"):
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=60,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# django cors headers settings
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "false").lower() in {
    "1",
    "true",
    "yes",
}

# custom user model
AUTH_USER_MODEL = 'accounts.User'

# Persistent site-wide sessions. Secure-cookie behavior is explicit so HTTP
# development is not accidentally configured with cookies the browser refuses
# to send.
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_SESSION_COOKIE_AGE", "1209600"))
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_PATH = "/"
SESSION_COOKIE_SECURE = os.getenv(
    "DJANGO_SESSION_COOKIE_SECURE", "false"
).lower() in {"1", "true", "yes"}
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = os.getenv(
    "DJANGO_CSRF_COOKIE_SECURE", "false"
).lower() in {"1", "true", "yes"}


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files config

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles/'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL = '/assets/'
MEDIA_ROOT = BASE_DIR / "assets"
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
# # static root
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Scholarly metadata provider. OpenAlex is the default because it offers a
# documented API and a free daily allowance. SerpAPI remains an opt-in fallback.
SCHOLAR_DATA_PROVIDER = os.getenv("SCHOLAR_DATA_PROVIDER", "openalex")
OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SCHOLAR_HTTP_TIMEOUT = int(os.getenv("SCHOLAR_HTTP_TIMEOUT", "30"))
SCHOLAR_QUEUE_AUTOSTART = os.getenv(
    "SCHOLAR_QUEUE_AUTOSTART",
    "true" if DEBUG else "false",
).lower() in {"1", "true", "yes"}
SCHOLAR_QUEUE_POLL_SECONDS = float(
    os.getenv("SCHOLAR_QUEUE_POLL_SECONDS", "2")
)
SCHOLAR_USER_AGENT = os.getenv(
    "SCHOLAR_USER_AGENT",
    "UG-Scholar/1.0 (mailto:library@ug.edu.gh)",
)
