"""
Module with Exception definitions
"""
import requests


class ConfluenceError(Exception):
    """Corresponds to 413 errors on the REST API.
    """

    def __init__(self, path, params, response, msg=None):
        # type: (str, dict, requests.Response, [str]) -> None
        if not msg:
            msg = 'General resource error accessing path {}'.format(path)
        self.path = path
        self.params = params
        self.response = response
        super(ConfluenceError, self).__init__(msg)


class ConfluencePermissionError(ConfluenceError):
    """Corresponds to 403 errors on the REST API.
    """

    def __init__(self, path, params, response):
        # type: (str, dict, requests.Response) -> None
        msg = 'User has insufficient permissions to perform ' \
              'that operation on the path {}'.format(path)
        super(ConfluencePermissionError, self).__init__(path, params, response, msg)


class ConfluenceNotFoundError(ConfluenceError):
    """Corresponds to 404 errors on the REST API.
    """

    def __init__(self, path, params, response):
        # type: (str, dict, requests.Response) -> None
        msg = "Confluence Content Not Found: '{}'".format(response.text)
        super(ConfluenceNotFoundError, self).__init__(path, params, response, msg)


class HttpError(Exception):
    """Corresponds to 413 errors on the REST API.
    """

    def __init__(self, path, params, response, msg=None):
        # type: (str, dict, requests.Response, [str]) -> None
        if not msg:
            msg = 'General resource error accessing path {}'.format(path)
        self.path = path
        self.params = params
        self.response = response
        super(HttpError, self).__init__(msg)


class HttpNotFoundError(HttpError):
    """Corresponds to 404 errors on the HTTP REST API.
    """

    def __init__(self, path, params, response):
        # type: (str, dict, requests.Response) -> None
        msg = "HTTP Content Not Found: '{}'".format(response.text)
        super(HttpNotFoundError, self).__init__(path, params, response, msg)
