from . import base

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


