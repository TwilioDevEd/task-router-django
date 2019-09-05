'''
Test settings

- Run in Debug mode
'''

from .common import *  # noqa

# Turn on DEBUG for tests
DEBUG = True

# Custom flag to avoid setuping the TaskRouter when the app starts
TESTING = True
