import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'p&grn73^$c!ae=o)igek_rn2t#(_sb9g1kqwxcpv16-ie__1=1'

DEBUG = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'premis_event_service',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

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
if os.getenv('PES_BACKEND') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'OPTIONS': {
                'init_command': 'SET storage_engine=MyISAM'
            }
        }
    }
    DATABASES['default']['NAME'] = 'premis_local'
    DATABASES['default']['USER'] = 'root'
    DATABASES['default']['PASSWORD'] = 'root'
    DATABASES['default']['HOST'] = 'db'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':  os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

ROOT_URLCONF = 'tests.urls'

LANGUAGE_CODE = 'en-us'

USE_I18N = True

USE_L10N = True

STATIC_URL = '/static/'

MAINTENANCE_MSG = None
