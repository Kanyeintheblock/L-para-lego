from pathlib import Path
from django.contrib.messages import constants as message_constants

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD ---
# IMPORTANTE: No compartas tu SECRET_KEY.
SECRET_KEY = 'django-insecure-(w0l(o!qmnniszv(9hmrz7x%!(xw2%76b*^bbo*xn!(89a@#+l'

# DEBUG=True solo para desarrollo. ¡Cámbialo a False en producción!
DEBUG = True
ALLOWED_HOSTS = []

# --- APLICACIONES ---
INSTALLED_APPS = [
    "unfold",  # DEBE IR PRIMERO
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ventas',  # Tu aplicación principal
]

# --- MIDDLEWARE ---
# Procesan las peticiones antes de llegar a las vistas (seguridad, sesiones, etc.)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'movilnet_config.urls'

# --- PLANTILLAS (TEMPLATES) ---
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

WSGI_APPLICATION = 'movilnet_config.wsgi.application'

# --- BASE DE DATOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gestion_de_seguimiento',
        'USER': 'postgres',
        'PASSWORD': '1234', # TODO: Mover a variables de entorno (.env)
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}

# --- VALIDACIÓN DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- IDIOMA Y TIEMPO ---
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS ---
STATIC_URL = 'static/'

# --- AUTENTICACIÓN ---
LOGIN_URL = 'login_usuario'

# --- CONFIGURACIÓN DE MENSAJES (Notificaciones al usuario) ---
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger', 
}
UNFOLD = {
    "SITE_TITLE": "Movilnet Gestión",
    "SITE_HEADER": "MI MOVILNET",
    "COLORS": {
        "primary": {
            "50": "255 241 242",
            "100": "255 225 227",
            "200": "255 197 200",
            "300": "255 153 158",
            "400": "255 88 95",  # <--- AQUÍ ESTÁ TU COLOR #ff585f
            "500": "255 88 95",
            "600": "229 79 86",
            "700": "191 66 71",
            "800": "153 53 57",
            "900": "127 44 47",
            "950": "76 26 28",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}