# Minimalistic settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = "=================================================="

DEBUG = True

os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"

GETPAID_ORDER_MODEL = "orders.Order"
GETPAID_PAYMENT_MODEL = "orders.CustomPayment"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "getpaid",
    "getpaid_payu",
    "orders",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

GETPAID_BACKEND_SETTINGS = {
    "paynow": {  # dotted import path of the plugin
        # refer to backend docs for its real settings
        "api_key": "d2e1d881-40b0-4b7e-9168-181bae3dc4e0",
        # "api_key": "9bcdead5-b194-4eb5-a1d5-c1654572e624",
        # "signature_key": "54d22fdb-2a8b-4711-a2e9-0e69a2a91189",
        "signature_key": "8e42a868-5562-440d-817c-4921632fb049",
    },
}
