'''
Default values for various app-defined settings

Formula: FOO = getattr(settings, 'FOO', "default_value")

These settings values will be used only if they are not found in the project
settings.py module. If you want to override any of these values, just redefine
them in that file rather than here.
'''
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

ROOT_URLCONF = 'tests.urls'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

# USE_TZ = True

STATIC_URL = '/static/'

MAINTENANCE_MSG = None

# Used in codalib/util.py
EVENT_ID_TYPE_XML = \
        "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#UUID"
LINK_AGENT_ID_TYPE_XML = \
    "http://purl.org/net/untl/vocabularies/identifier-qualifiers/#URL"
LINK_AGENT_ID_ROLE_XML = \
    "http://id.loc.gov/vocabulary/preservation/eventRelatedAgentRole/exe"

# Used in codalib/bagatom.py
BAGATOM_BAG_NAMESPACE = "TODO"
BAGATOM_QXML_NAMESPACE = "TODO"
BAGATOM_NODE_NAMESPACE = "TODO"

# Used in forms.py
EVENT_OUTCOME_CHOICES = (
    ('', 'None'),
    ('http://purl.org/net/untl/vocabularies/eventOutcomes/#success', 'Success'),
    ('http://purl.org/net/untl/vocabularies/eventOutcomes/#failure', 'Failure'),
)

EVENT_TYPE_CHOICES = (
    ('', 'None'),
    ('http://id.loc.gov/vocabulary/preservation/eventType/fix', 'Fixity Check'),
    ('http://id.loc.gov/vocabulary/preservation/eventType/rep', 'Replication'),
    ('http://id.loc.gov/vocabulary/preservation/eventType/ing', 'Ingestion'),
    ('http://id.loc.gov/vocabulary/preservation/eventType/mig', 'Migration'),
)
