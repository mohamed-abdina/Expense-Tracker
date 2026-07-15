# This app intentionally has no custom models.
#
# The spec's User fields (id, username, email, password, date_joined) map
# directly onto Django's built-in django.contrib.auth.models.User, so we
# use that directly instead of duplicating it. If you later need extra
# profile fields (avatar, currency preference, etc.), add a Profile model
# here with a OneToOneField to settings.AUTH_USER_MODEL.
