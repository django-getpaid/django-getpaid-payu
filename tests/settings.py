# Minimalistic settings
import os

os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "=================================================="

DEBUG = True

GETPAID_ORDER_MODEL = "orders.Order"

GETPAID_BACKEND_SETTINGS = {
    "getpaid_payu": {
        "pos_id": 300746,
        "second_key": "b6ca15b0d1020e8094d9b5f8d163db54",
        "client_id": 300746,
        "client_secret": "2ee86a66e5d97e3fadc400c9f19b065d",
        "confirmation_method": "PULL",
        "method": "REST",
    },
}

PAYWALL_MODE = "PAY"  # PAY for instant paying, LOCK for pre-auth

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django_fsm",
    "getpaid",
    "getpaid_payu",
    "orders",
    "paywall",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ]
        },
    }
]

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "db.sqlite3"}}

TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True
