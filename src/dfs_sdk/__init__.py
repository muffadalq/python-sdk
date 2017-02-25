"""
Python package for interacting with the REST interface of a Datera
storage cluster.
"""
__copyright__ = "Copyright 2015, Datera, Inc."


from .api_v2 import DateraApi
from .api_v2_1 import DateraApi21
from .exceptions import ApiError
from .exceptions import ApiAuthError
from .exceptions import ApiInvalidRequestError
from .exceptions import ApiNotFoundError
from .exceptions import ApiConflictError
from .exceptions import ApiConnectionError
from .exceptions import ApiTimeoutError
from .exceptions import ApiInternalError
from .exceptions import ApiUnavailableError


def get_api(hostname, username, password, version, tenant=None):
    """
    Returns a DateraApi object
    Parameters:
      hostname (str) - The hostname or VIP
      username (str) - e.g. "admin"
      password (str)
      version (str) - must be "v2" or "v2.1"
    Optional parameters:
      tenant (str) - Tenant, for v2.1 API only
    """
    if version == "v2":
        if tenant:
            raise ValueError("API version v2 does not support multi-tenancy")
        return DateraApi(hostname, username, password)
    elif version == "v2.1":
        return DateraApi21(hostname, username, password, tenant=tenant)
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
           'DateraApi',
           'DateraApi21']
