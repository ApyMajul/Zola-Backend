"""
Project Django settings

all environment-specific settings modules (development, preprod, production and
docker_local) star-import everything for the base module, so generic settings
should always be set in the base module.
"""

from .development import *
