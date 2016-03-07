"""
Python package for interacting with the REST interface of a Datera
storage cluster.
"""
__copyright__ = "Copyright 2015, Datera, Inc."


from .types_v2 import *
from .api_v2 import DateraApi
from .exceptions import ApiError
from .exceptions import ApiAuthError
from .exceptions import ApiNotFoundError, ApiConflictError
from .exceptions import ApiConnectionError, ApiTimeoutError
from .exceptions import ApiInternalError, ApiUnavailableError
from .exceptions import ApiInvalidRequestError


def get_api(hostname, username, password, version):
    """
    Returns a DateraApi object
    Parameters:
      hostname (str) - The hostname or VIP
      username (str) - e.g. "admin"
      password (str)
      version (str) - must be "v2"
    """
    if version == "v2":
        return DateraApi(hostname, username, password)
    else:
        raise NotImplementedError("Unsupported API version: " + repr(version))


__all__ = ['get_api',
           'ApiError',
           'ApiAuthError',
           'ApiInvalidRequestError',
           'ApiNotFoundError',
           'ApiConflictError',
           'ApiConnectionError',
           'ApiTimeoutError',
           'ApiInternalError',
           'ApiUnavailableError',
           'DateraApi']
