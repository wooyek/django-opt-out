# coding=utf-8

from django.conf import settings

# This will be used as a prefix when generating opt-out urls
# You cane leave it blank and set full path URL by yourself
OPT_OUT_BASE_URL = None

# If you set this to false we'll not validate that user actually used our opt-out url
# thus do not require confirmation of email address ownership.
# Anyone will be able to opt-pot anyone else.
OUT_OUT_REQUIRE_CONFIRMATION = True

# This is a secret for password generation
# We don use strong password hasher and email is the password base
# so you may want to use here something other than SECRET_KEY to not compromise main secret security
OPT_OUT_SECRET = settings.SECRET_KEY[::4]

# to validate that user actually got our message we put passwords int he opt-out url
# these have minimal security to we keep them simple and short
OPT_OUT_PASSWORD_HASHER = 'default'

# a custom view with goodbye message and suggestion to reconsider and change user feedback
# This view url must be similar to the OptOutSuccess view url
# It should not drop usage of secret as it ensures that a visitor is authenticated
# When providing your own please consider using OptOutBase as view base class
OPT_OUT_GOODBYE_VIEW = None

# a list of backends that should get enabled during application initialization
OPT_OUT_BACKENDS = []
