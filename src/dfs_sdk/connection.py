"""
Provides the ApiConnection class
"""
__copyright__ = "Copyright 2015, Datera, Inc."

import sys
import logging
import socket
import json
import threading
import functools
import collections
import ssl

from .exceptions import ApiError
from .exceptions import ApiAuthError, ApiConnectionError, ApiTimeoutError
from .exceptions import ApiInternalError, ApiNotFoundError
from .exceptions import ApiInvalidRequestError, ApiConflictError
from .constants import REST_PORT, REST_PORT_HTTPS, DEFAULT_HTTP_TIMEOUT

from .constants import PYTHON_2_7_0_HEXVERSION
from .constants import PYTHON_2_7_9_HEXVERSION
from .constants import PYTHON_3_0_0_HEXVERSION

if sys.hexversion >= PYTHON_3_0_0_HEXVERSION:
    # Python 3
    from http.client import HTTPConnection  # noqa pylint: disable=import-error
    from http.client import HTTPException  # noqa pylint: disable=import-error
    # noqa pylint: disable=import-error
    from http.client import HTTPSConnection
    # noqa pylint: disable=import-error,no-name-in-module
    from urllib.parse import quote as encode_url
else:
    # Python 2
    from httplib import HTTPConnection  # noqa pylint: disable=import-error
    from httplib import HTTPException  # noqa pylint: disable=import-error
    from httplib import HTTPSConnection  # noqa pylint: disable=import-error
    from urllib import quote as encode_url  # noqa pylint: disable=import-error

LOG = logging.getLogger(__name__)
if sys.hexversion >= PYTHON_2_7_0_HEXVERSION:
    if not LOG.handlers:
        LOG.addHandler(logging.NullHandler())


def _with_authentication(method):
    """
    Decorator to wrap Api method calls so that we login again if our key
    expires.
    """
    @functools.wraps(method)
    def wrapper_method(self, *args, **kwargs):
        """ Call the original method with a re-login if needed """
        # if we haven't logged in yet, log in and then try the method:
        if not self._logged_in:
            self._logger.debug("Log in to API...")
            self.login()
            return method(self, *args, **kwargs)
        # already logged in, but retry if needed in case the key expires:
        try:
            return method(self, *args, **kwargs)
        except ApiAuthError:
            self._logger.debug("API auth error, so try to log in again...")
            self.login()
            return method(self, *args, **kwargs)
    return wrapper_method


def _make_unicode_string(inval):
    """
    Converts a string or bytes into a UTF-8 unicode string
    """
    try:
        return unicode(inval, 'utf-8')  # Python2
    except NameError:
        return str(inval, 'utf-8')      # Python3


class ApiConnection(object):
    """
    This class wraps the HTTP connection, translates to/from JSON, and
    handles authentication.
    Its methods raise ApiError (or its subclasses) when things go wrong
    """

    def __init__(self, context):
        """
        Parameters:
          hostname (str) - IP address or host name
          username (str) - Username to log in with, e.g. "admin"
          password (str) - Password to use when logging in to the cluster
          timeout (float) - HTTP connection  timeout.  If None, use system
                            default.
          secure (boolean) - Use HTTPS instead of HTTP. Defaults to HTTPS
        """
        self._logger = logging.getLogger(__name__)
        if not self._logger.handlers:
            self._logger.addHandler(logging.NullHandler())

        self._context = context
        self._hostname = context.hostname
        self._username = context.username
        self._password = context.password

        self._version = context.version

        self._secure = context.secure
        if self._secure is False:
            self._port = REST_PORT
        else:
            self._port = REST_PORT_HTTPS
        self._timeout = context.timeout

        self._lock = threading.Lock()
        self._key = None
        self._logged_in = False

    def _get_http_connection(self, hostname, port,
                             timeout=DEFAULT_HTTP_TIMEOUT, secure=True):
        """
        Returns an HTTPConnection instance
        """
        if self._secure:
            if sys.hexversion >= PYTHON_2_7_9_HEXVERSION:
                sslcontext = ssl._create_unverified_context()
                conn = HTTPSConnection(hostname, port=port, timeout=timeout,
                                       context=sslcontext)
            else:
                conn = HTTPSConnection(hostname, port=port, timeout=timeout)
        else:
            conn = HTTPConnection(hostname, port=port, timeout=timeout)
        return conn

    def _http_connect_request(self, hostname, port, method, urlpath,
                              params=None, body=None, headers=None):
        """
        Sends the HTTP request
        Parameters:
          hostname (str)
          port (int)
          method (str) - "GET", "POST", ...
          urlpath (str) - e.g. "/v2/system"
          headers (dict)
          body (str)
        Returns a (resp_data, resp_status, resp_reason, reap_headers) tuple
          resp_data (str)
          resp_status (int)
          resp_reason (str)
          resp_headers - list of (key, val) tuples
        Raises ApiTimeoutError or ApiConnectionError on connection error.
        Raises an ApiError subclass on all other errors
        """
        if not urlpath.startswith('/'):
            raise ValueError("Invalid URL path")

        # Handle special characters present between the path.
        # A IQN name can contain special characters (".", "-", ":") hence
        # skipping them from encoding.(Ref. RFC3720)
        urlpath = encode_url(urlpath, safe='/:.-')

        if params:
            count = 0
            for key in params.keys():
                if count > 0:
                    urlpath += "&"
                if count == 0:
                    urlpath += "?"
                cmd = "=".join([key, encode_url(params[key])])
                urlpath += cmd
                count += 1

        if headers is None:
            headers = {}

        try:
            conn = self._get_http_connection(hostname, port,
                                             timeout=self._timeout,
                                             secure=self._secure)
            self._logger.debug("REST send: method=" + str(method) +
                               " hostname=" + str(hostname) +
                               " port=" + str(port) +
                               " urlpath=" + str(urlpath) +
                               " headers=" + str(headers) +
                               " body=" + str(body))
            conn.request(method, urlpath, body=body, headers=headers)
            resp = conn.getresponse()
            resp_status = resp.status     # e.g. 200
            resp_reason = resp.reason    # e.g. 'OK'
            resp_headers = resp.getheaders()   # list of (key,val) tuples
            resp_data = resp.read()
            conn.close()
        except (socket.error, HTTPException) as ex:
            # If network error, raise exception:
            msg = str(ex)
            msg += "\nIP: " + str(self._hostname)
            if isinstance(ex, socket.timeout):
                exclass = ApiTimeoutError
            else:
                exclass = ApiConnectionError
            raise exclass, exclass(msg), sys.exc_info()[-1]
        # Debug log response:
        msg = "REST recv: status=" + str(resp_status) + \
              " reason=" + str(resp_reason) + \
              " headers=" + str(resp_headers) + \
              " data=" + str(resp_data)
        self._logger.debug(msg)
        # If API returned an error, raise exception:
        self._assert_response_successful(method, urlpath, body,
                                         resp_data, resp_status, resp_reason)
        return (resp_data, resp_status, resp_reason, resp_headers)

    def login(self, **params):
        """ Login to the API, store the key """
        if params:
            send_data = {
                "name": params.get("name"), "password": params.get("password")}
        else:
            send_data = {"name": self._username, "password": self._password}
        body = json.dumps(send_data)

        headers = dict()
        headers["content-type"] = "application/json; charset=utf-8"
        urlpath = "/" + self._version + "/login"
        method = "PUT"
        resp_data, resp_status, resp_reason, resp_hdrs = \
            self._http_connect_request(self._hostname, self._port,
                                       method, urlpath, body=body,
                                       headers=headers)
        resp_data = _make_unicode_string(resp_data)
        try:
            resp_dict = json.loads(resp_data)
        except ValueError:
            raise ApiError("Login failed: " + repr(resp_data))

        if 'key' not in resp_dict or not resp_dict['key']:
            raise ApiAuthError("No auth key returned", resp_data)
        key = str(resp_dict['key'])
        with self._lock:
            self._key = key
            self._logged_in = True

    def logout(self):
        """ Perform logout operation with the key"""
        with self._lock:
            key = self._key
            self._key = None
            self._logged_in = False
        headers = dict()
        headers["content-type"] = "application/json; charset=utf-8"
        headers["auth-token"] = key
        urlpath = "/" + self._version + "/logout"
        method = "PUT"
        self._http_connect_request(self._hostname, self._port,
                                   method, urlpath, headers=headers)

    @property
    def auth_key(self):
        return self._key

    @auth_key.setter
    def auth_key(self, new_key):
        self._key = new_key

    def _assert_response_successful(self, method, urlpath, body,
                                    resp_data, resp_status, resp_reason):
        """ Raises an exception if the response was an error """
        if resp_status < 200 or resp_status > 299:
            msg = "[REQUEST]: " + method + " " + urlpath + "\n"
            if body is not None:
                msg += str(body) + "\n"
            if resp_data:
                msg += '[RESPONSE]: '
                msg += str(resp_data) + "\n"
            msg += str(resp_status) + " " + str(resp_reason)
            if resp_status == 401:
                raise ApiAuthError(msg, resp_data)
            elif resp_status == 404:
                raise ApiNotFoundError(msg, resp_data)
            elif resp_status == 400 or resp_status == 405 or \
                    resp_status == 403 or resp_status == 422:
                raise ApiInvalidRequestError(msg, resp_data)
            elif resp_status == 409:
                raise ApiConflictError(msg, resp_data)
            elif resp_status == 500 or resp_status == 503:
                raise ApiInternalError(msg, resp_data)
            else:
                raise ApiError(msg, resp_data)

    @_with_authentication
    def _do_request(self, method, urlpath, data=None, params=None):
        """
        Translates to/from JSON as needed, calls _http_connect_request()
        Raises ApiError on error
        """
        headers = dict()
        if self._key:
            headers["Auth-Token"] = self._key
        headers["content-type"] = "application/json; charset=utf-8"
        if data is None:
            body = None
        elif isinstance(data, str):
            body = data
        else:
            body = json.dumps(data)  # can raise ValueError

        resp_data, resp_status, resp_reason, _resp_headers = \
            self._http_connect_request(self._hostname, self._port,
                                       method, urlpath, params=params,
                                       body=body, headers=headers)
        if resp_data is None:
            return None
        elif resp_data == "":
            return None
        else:
            resp_data = _make_unicode_string(resp_data)
            return json.loads(resp_data,
                              object_pairs_hook=collections.OrderedDict)

    ########################################

    def create_entity(self, path, data):
        """
        Returns the parsed response data
        Raises ApiError on error
        Parameters:
          path (str) - Endpoint path, e.g. "/app_templates"
          data (dict) - e.g. {"name": "myapptemplate"}
        """
        urlpath = "/" + self._version + path
        return self._do_request("POST", urlpath, data=data)

    def read_endpoint(self, path, params=None):
        """
        Returns the parsed response data
        Raises ApiError on error
        Parameters:
          path (str) - Endpoint path, e.g. "/app_templates"
          params (dict) - Querry Params, e.g. "/app_templates?key=value"
        """
        urlpath = "/" + self._version + path
        return self._do_request("GET", urlpath, params=params)

    def read_entity(self, path, params=None):
        """
        Returns the parsed response data
        Raises ApiError on error
        Parameters:
          path (str) - Entity path, e.g. "/app_templates/myapptemplate"
          params (dict) - Querry Params, e.g. "/app_templates?key=value"
        """
        urlpath = "/" + self._version + path
        return self._do_request("GET", urlpath, params=params)

    def update_endpoint(self, path, data):
        """
        Returns the parsed response data
        Raises ApiError on error
        Parameters:
          path (str) - Endpoint path
          data (dict)
        """
        urlpath = "/" + self._version + path
        return self._do_request("PUT", urlpath, data=data)

    def update_entity(self, path, data):
        """
        Returns the parsed response data
        Raises ApiError on error
        Parameters:
          path (str) - Entity path, e.g. "/app_templates/myapptemplate"
          data (dict)
        """
        urlpath = "/" + self._version + path
        return self._do_request("PUT", urlpath, data=data)

    def delete_entity(self, path, data=None):
        """
        Returns the parsed response data
        Raises ApiError on HTTP error
        Parameters:
          path (str) - Entity path, e.g. "/app_templates/myapptemplate"
        """
        urlpath = "/" + self._version + path
        return self._do_request("DELETE", urlpath, data=data)
