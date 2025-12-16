from os import environ

SESSION_CONFIGS = [
    dict(
        name='framing_aesthetic',
        display_name='Framing & Aesthetic Usability Experiment',
        num_demo_participants=100,
        app_sequence=['framing_experiment'],
    ),
]

# ROOMS hinzufügen:
ROOMS = [
    dict(
        name='gruppe1',
        display_name='Gruppe 1',
        participant_label_file='_rooms/gruppe1.txt',
    ),
    dict(
        name='gruppe2',
        display_name='Gruppe 2',
        participant_label_file='_rooms/gruppe2.txt',
    ),
    dict(
        name='gruppe3',
        display_name='Gruppe 3',
        participant_label_file='_rooms/gruppe3.txt',
    ),
    dict(
        name='gruppe4',
        display_name='Gruppe 4',
        participant_label_file='_rooms/gruppe4.txt',
    ),
]
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'de'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'CHF'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '7453617464404'

INSTALLED_APPS = ['otree']