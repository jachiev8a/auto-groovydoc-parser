#!/usr/bin/env python
# coding=utf-8
"""
Module Base Api
"""

import logging
import requests
import abc

from confluence.exceptions import HttpNotFoundError

# main logger instance
LOGGER = logging.getLogger(__name__)


class BaseApi(object):
    """Base API class for application
    """

    def __init__(self, host_url, rest_api_url, user, password, headers=None):
        # type: (str, str, str, str, dict) -> BaseApi
        """

        :param host_url: URL of the REST API application
        :param rest_api_url: base url of the api.
            ex. /api/v1/
        :param user: name of the authentication user (existing in the server)
        :param password: password string of the user
        """
        # authentication credentials
        self._user = user
        self._password = password
        self._basic_auth = (user, password)
        self._headers = headers

        # validate host url path
        if host_url.endswith('/'):
            # remove / if host url has it at the end
            host_url = host_url[:-1]
        self._host_url = host_url

        # validate rest api path
        if not rest_api_url.startswith('/'):
            rest_api_url = '/' + rest_api_url

        # build base API URL with host name
        self._api_base_url = '{host}{rest_api_url}'.format(
            host=self._host_url,
            rest_api_url=rest_api_url)

    @staticmethod
    def _handle_response_errors(path, params, response):
        # type: (str, dict[str, str], requests.Response) -> None
        """Handles the response gotten from requests.Response instance
        to see if there is a problem in order to raise the exact exception

        """
        if response.status_code == 400:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 401:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 402:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 403:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 404:
            LOGGER.error("API Error: {}".format(response.text))
            raise HttpNotFoundError(path, params, response)
        elif response.status_code == 405:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 406:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 407:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 408:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)
        elif response.status_code == 500:
            LOGGER.error("API Error: {}".format(response.text))
            raise Exception(path, params, response)

    def _get(self, path, params):
        # type: (str, dict[str, str]) -> dict
        """HTTP GET method for Confluence Client api

        :param path: path to REST API to get content
        :param params: dictionary with the parameters
            to add to GET message.
        :param expand:
        :return:
        """
        url = '{}/{}'.format(self._api_base_url, path)
        # send GET request over client and expect response
        response = requests.get(
            url,
            params=params,
            headers=self._headers,
            auth=self._basic_auth
        )
        # validate HTTP response to handle possible errors
        self._handle_response_errors(path, params, response)
        return response.json()

    def _post(self, path, params, data, files=None):
        # type: (str, dict, dict, str) -> dict
        """HTTP POST method for Confluence Client api

        :param path: path to REST API to post content
        :param params: dictionary with the parameters
            to add to POST message.
        :param data: dictionary with the data to post
        :param files:
        :return:
        """
        # build base url with path
        url = "{}/{}".format(self._api_base_url, path)
        # send POST request over client and expect response
        response = requests.post(
            url,
            json=data,
            params=params,
            headers=self._headers,
            files=files,
            auth=self._basic_auth
        )
        # validate HTTP response to handle possible errors
        self._handle_response_errors(path, params, response)
        return response.json()

    def _put(self, path, params, data):
        # type: (str, dict[str, str], dict) -> dict
        """HTTP PUT method for Confluence Client api

        :param path: path to REST API to put content
        :param params: dictionary with the parameters
            to add to PUT message.
        :param data: dictionary with the data to put
        :return:
        """
        # build base url with path
        url = "{}/{}".format(self._api_base_url, path)
        response = requests.put(
            url,
            json=data,
            params=params,
            headers=self._headers,
            auth=self._basic_auth
        )
        # check HTTP response to handle errors
        self._handle_response_errors(path, params, response)
        return response.json()

    def _delete(self, path, params):
        # type: (str, dict) -> dict
        """HTTP DELETE method for client api

        :param path: path to REST API to delete content
        :param params: dictionary with the parameters for DELETE Method
        :return: None
        """
        # build base url with path
        url = "{}/{}".format(self._api_base_url, path)
        # send POST request over client and expect response
        response = requests.delete(
            url,
            params=params,
            headers=self._headers,
            auth=self._basic_auth
        )
        # check HTTP response to handle errors
        self._handle_response_errors(path, params, response)
        return response.json()


class Content(object):
    """Base Class for classes related for Confluence Content
    ex. Confluence Page
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, json_data):
        # type: (dict) -> Content
        self._json_data_model = json_data

    @property
    def json_data_model(self):
        # type: () -> dict
        """Returns a dictionary with the json data model
        retrieved from HTTP response
        """
        return self._json_data_model

    @abc.abstractmethod
    def _retrieve_values_from_json(self):
        # type: () -> None
        raise NotImplementedError("abstract method not implemented in child!")
