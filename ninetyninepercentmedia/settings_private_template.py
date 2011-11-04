DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

# This is the only value you *must* set.  You can get a free embedly API
# key here: http://embed.ly/pricing/free
EMBEDLY_KEY = ''

LOCAL_INSTALLED_APPS = (
)

# Use these email settings when running the python debugging smtp server
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
