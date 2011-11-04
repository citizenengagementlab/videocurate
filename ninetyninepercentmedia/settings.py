import os,sys
from os.path import join

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])
PROJECT_ROOT = os.path.join(PROJECT_PATH,'../')
sys.path.insert(0, PROJECT_ROOT)

# Django settings for ninetyninepercentmedia project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Josh Levinger', 'josh.l@engagementlab.org'),
     ('Ben Wilkins','ben.w@engagementlab.org')
)
EMAIL_SUBJECT_PREFIX = "[99PercentMedia] "

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '99percentmedia.db',     # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT,'static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'secretballot.middleware.SecretBallotIpMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'ninetyninepercentmedia.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT,'ninetyninepercentmedia/templates'),
    os.path.join(PROJECT_ROOT,'mediacurate/templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'django.contrib.humanize',

    #external dependencies
    'embeds',
    'secretballot',
    'tagging',
    'tagging_autocomplete',
    'form_utils',
    'django_countries',
    'ajaxcomments',
    'django_antichaos',

    #internal apps
    'mediacurate',
)

# debug toolbar
INTERNAL_IPS = ('127.0.0.1','75.101.48.104')
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

try:
    from settings_private import *
except ImportError:
    print '''Can't find settings_private.py
    Proceeding with default values for DATABASES, and EMBEDLY_KEY
    You probably want to define your own'''
    EMBEDLY_KEY = ''

# Allow private_setings.py to define LOCAL_INSTALLED_APPS.
INSTALLED_APPS = tuple(list(INSTALLED_APPS) + list(LOCAL_INSTALLED_APPS))

# Generate a local secret key.
if not 'SECRET_KEY' in locals():
    from random import choice
    SECRET_KEY = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    fname = os.path.join(os.path.dirname(__file__), 'settings_private.py')
    f = open(fname, 'a')
    f.write("SECRET_KEY = '%s'" % SECRET_KEY)
    f.close()
