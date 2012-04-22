
# Debugging on
DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
