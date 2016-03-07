"""
Provides the v2 DateraApi object
"""
__copyright__ = "Copyright 2015, Datera, Inc."


from .constants import DEFAULT_NETWORK_TIMEOUT
from .connection import ApiConnection
from .context import ApiContext
from .types_v2 import RootEp

API_VERSION = "v2"


class DateraApi(RootEp):
    """
    Use this object to talk to the REST interface of a Datera cluster
    """

    def __init__(self, hostname, username=None, password=None,
                 timeout=DEFAULT_NETWORK_TIMEOUT,
                 immediate_login=True,
                 secure=True):
        """
        Parameters:
          hostname (str) - IP address or host name
          username (str) - Username to log in with, e.g. "admin"
          password (str) - Password to use when logging in to the cluster
          timeout (float) - HTTP connection  timeout.  If None, use system
                            default.
          secure (boolean) - Use HTTPS instead of HTTP, defaults to HTTPS
          immediate_login (bool) - If True, login when this object is
                                   instantiated, else wait to login until
                                   a request is sent
        """
        if not hostname or not username or not password:
            raise ValueError("hostname, username, and password are required")

        # Create the context object, common to all endpoints and entities:
        self._context = self._create_context(hostname,
                                             username=username,
                                             password=password,
                                             timeout=timeout,
                                             secure=secure)

        if immediate_login:
            self._context.connection.login(name=username, password=password)

        # Initialize sub-endpoints:
        super(DateraApi, self).__init__(self._context, None)

    def _create_context(self, hostname, username=None, password=None,
                        timeout=None, secure=True):
        """
        Creates the context object
        This will be attached as a private attribute to all entities
        and endpoints returned by this API.

        Note that this is responsible for creating a connection object,
        which is an attribute of the context object.
        """
        context = ApiContext()
        context.version = API_VERSION

        context.hostname = hostname
        context.username = username
        context.password = password

        context.timeout = timeout
        context.secure = secure

        context.connection = self._create_connection(context)
        return context

    def _create_connection(self, context):
        """
        Creates the API connection object used to communicate over REST
        """
        return ApiConnection(context)
