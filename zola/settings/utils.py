"""Utilities for settings management."""

from pathlib import Path
from os import getenv

from whitenoise.storage import CompressedManifestStaticFilesStorage


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """
    Disables the manifest_strict
    (https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.ManifestStaticFilesStorage.manifest_strict)
    attribute on the whitenoise storage class (to avoid raising an Exception
    when a static file isn't found).
    """
    manifest_strict = False


def get_secret(secret_name, secrets_directory="/etc/secrets"):
    """
    Returns a kubernetes from a file.
    """
    if bool(getenv('LEVIATHAN_BUILD', None)):
        # If the build environment is switched on, don't try to read the secret
        # and return a placeholder instead. This is so running manage commands
        # (i.e. collectstatic) can be used during build.
        return "PLACEHOLDER"
    secret_file = Path(secrets_directory) / secret_name
    with open(secret_file, 'r') as f:
        secret_value = f.read().strip()
    return secret_value
