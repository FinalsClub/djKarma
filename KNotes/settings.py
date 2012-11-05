# settings.py is part of Karma Notes
# Django settings for KNotes project.

''' Secrets '''
from notes.credentials import FACEBOOK_ID
from notes.credentials import FACEBOOK_SECRET

from notes.credentials import BETA_DB_NAME
from notes.credentials import BETA_DB_USERNAME
from notes.credentials import BETA_DB_PASSWORD

from notes.credentials import PROD_DB_NAME
from notes.credentials import PROD_DB_USERNAME
from notes.credentials import PROD_DB_PASSWORD

from notes.credentials import DEV_STATIC_ROOT
from notes.credentials import BETA_STATIC_ROOT
from notes.credentials import PROD_STATIC_ROOT

from notes.credentials import DEV_UPLOAD_ROOT
from notes.credentials import BETA_UPLOAD_ROOT
from notes.credentials import PROD_UPLOAD_ROOT

from notes.credentials import RECAPTCHA_PRIVATE_KEY

from notes.credentials import SMTP_USERNAME
from notes.credentials import SMTP_PASSWORD

from notes.credentials import DEFAULT_FROM_EMAIL

import os
import djcelery

djcelery.setup_loader()

# Is this running on the karmanotes.org box?
DEPLOY = False
# Is this deployed as the beta server?
BETA = False

if DEPLOY:
    if not BETA:
        DEBUG = False

        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': PROD_DB_NAME,
            'USER': PROD_DB_USERNAME,
            'PASSWORD': PROD_DB_PASSWORD,
            'HOST': 'localhost',
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
            }
        }
    else:
        DEBUG = True

        DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': BETA_DB_NAME,
        'USER': BETA_DB_USERNAME,
        'PASSWORD': BETA_DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }


else:
    DEBUG = True

    # Local sqlite3 db config
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'karmaNotes.sql',
        }
    }

    # Local static file hosting
    # TODO: configure django to host local static files when in dev mode, but to rely on nginx in deployment
    #       Static file midlewares and helpers should be disabled in production

TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ("Seth Woodworth", 'seth@finalsclub.org'),
     ("David Brodsky", 'david@finalsclub.org')
)

MANAGERS = ADMINS

# For autocomplete
SIMPLE_AUTOCOMPLETE_MODELS = ('notes.School', 'notes.Course')

TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DEFAULT_FILE_STORAGE = 'notes.testStorage.TestFileSystemStorage'

# Used to store pks of uploaded but unclaimed files
# So an anon user can signup and claim the files / karma
# ... if the session still exists
SESSION_UNCLAIMED_FILES_KEY = 'unclaimed_files'

# This is the username to be get_or_created and assigned
# to File.owner when an uploaded file is recieved from
# a user with .is_authenticated() returning False (see local.py)
# in django-ajax-uploader
# File.save will not award karma to this username, so the file
# can be claimed for karma if the anon user logs in / registers
DEFAULT_UPLOADER_USERNAME = 'KarmaNotes'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
if DEPLOY:
    if BETA:
        MEDIA_ROOT = BETA_UPLOAD_ROOT
    else:
        MEDIA_ROOT = PROD_UPLOAD_ROOT
else:
    MEDIA_ROOT = DEV_UPLOAD_ROOT

# For Ajax Uploader
UPLOAD_DIR = MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://karmanotes.org/library/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
if DEPLOY:
    if BETA:
        STATIC_ROOT = BETA_STATIC_ROOT
    else:
        STATIC_ROOT = PROD_STATIC_ROOT
else:
    # This should work for any development machine's local path setting
    STATIC_ROOT = DEV_STATIC_ROOT


# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #DEV_APP_STATIC_ROOT,

    # this should work genericly
    os.path.join(os.path.dirname(__file__), '../static/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'uyvhruu^9#o*jdns^sxx(@yibo9ia%xjuk8@)u48bo!d$$%i_w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

######################
# Begin Auth Settings
#######################

AUTHENTICATION_BACKENDS = (
#   Auth backends courtesy django-social-auth

#   'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
#    'social_auth.backends.google.GoogleOAuthBackend',
#    'social_auth.backends.google.GoogleOAuth2Backend',
#    'social_auth.backends.google.GoogleBackend',
#    'social_auth.backends.yahoo.YahooBackend',
#    'social_auth.backends.browserid.BrowserIDBackend',
#    'social_auth.backends.contrib.linkedin.LinkedinBackend',
#    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
#    'social_auth.backends.contrib.orkut.OrkutBackend',
#    'social_auth.backends.contrib.foursquare.FoursquareBackend',
#    'social_auth.backends.contrib.dropbox.DropboxBackend',
#    'social_auth.backends.contrib.flickr.FlickrBackend',
#    'social_auth.backends.contrib.instagram.InstagramBackend',
#    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Tell Django where our UserProfile is defined
AUTH_PROFILE_MODULE = 'notes.UserProfile'

SOCIAL_AUTH_DEFAULT_USERNAME = 'noteworthy_notetaker'

#LOGIN_URL          = '/login/'
LOGIN_REDIRECT_URL = '/profile'
#LOGIN_ERROR_URL    = '/login/'

#If we want a different redirect for social login:
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/profile'
SOCIAL_AUTH_COMPLETE_URL_NAME  = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'

FACEBOOK_APP_ID              = FACEBOOK_ID
FACEBOOK_API_SECRET          = FACEBOOK_SECRET

# define additional data to request from FB
FACEBOOK_EXTENDED_PERMISSIONS = ['email', 'user_education_history']

######################
# End Auth Settings
#######################

ROOT_URLCONF = 'KNotes.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'KNotes.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    # Wherever you go, there you are
    os.path.join(os.path.dirname(__file__), 'templates'),
    './KNotes/templates/models',
    './KNotes/templates/modal',
    './KNotes/templates/ajax',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",  # Makes request accessible to templates
    "django.core.context_processors.static",  # Makes STATIC_URL available
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    # 3rd party packages
    'simple_autocomplete',
    'social_auth',
    'south',
    'gunicorn',
    'simplemathcaptcha',
    'ajaxuploader',  # Ajax fileUpload
    'djcelery',     # Django-Celery apps:
    'kombu.transport.django',
    'haystack',

    # our app(s)
    'notes',
)

# Django-Celery settings
BROKER_URL = "django://"

if DEPLOY:
    if BETA:
        CELERY_RESULT_DBURI = "postgresql://{0}:{1}@localhost/{2}".format(BETA_DB_USERNAME, BETA_DB_PASSWORD, BETA_DB_NAME)
    else:
        CELERY_RESULT_DBURI = "postgresql://{0}:{1}@localhost/{2}".format(PROD_DB_USERNAME, PROD_DB_PASSWORD, PROD_DB_NAME)
else:
    CELERY_RESULT_DBURI = "sqlite:///karmaNotes.sql"


### HAYSTACK Configuration
HAYSTACK_SITECONF = 'notes.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'

# Don't yet know if we'll be running 'multicore'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr'
# ...or for multicore...
#HAYSTACK_SOLR_URL = 'http://127.0.0.1:8983/solr/mysite'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

EMAIL_USE_TLS       = True
EMAIL_HOST          = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER     = SMTP_USERNAME
EMAIL_HOST_PASSWORD = SMTP_PASSWORD
EMAIL_PORT          = 587

TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/'  # use '' for top level template dir, ensure there is a trailing slash
TEMPLATED_EMAIL_FILE_EXTENSION = 'email'

try:
    # For development, mv the initial file `dev_settings.py` to be named `local_settings.py`
    from local_settings import *
except ImportError:
    pass
