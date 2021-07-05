#!/usr/bin/env python
# coding=utf-8
"""
Module with the ConfluenceClient class that can be instanced
in order to use the API
"""

import abc
import logging

from confluence.exceptions import ConfluenceError
from confluence.exceptions import ConfluencePermissionError
from confluence.exceptions import ConfluenceNotFoundError

from confluence.base_api import BaseApi
from confluence.base_api import Content

# main logger instance
LOGGER = logging.getLogger(__name__)


class ConfluenceApi(BaseApi):
    """Confluence Client API class

    An instance of this class is able to interact with the
    Confluence Server API in order to retrieve information
    or submit data into the server.

    This instance should be called within 'with' statement.
    Usage:

    with ConfluenceClient('http://host.com', 'user_x', 'pass_x') as instance:
        instance.get_content(...)
    """

    def __init__(self, confluence_url, user, password):
        # type: (str, str, str) -> None
        """

        :param confluence_url: confluence URL (with http extension)
            ex: http://confluence-server:8080
        :param user: name of the user (existing in the server)
        :param password: password string of the user
        """
        # Host and authentication credentials
        headers = {"X-Atlassian-Token": "nocheck"}
        super().__init__(confluence_url, "/rest/api", user, password, headers)

    def create_page(self, page_title, space_key, page_content,
                    parent_page_id=None, content_type='page'):
        # type: (str, str, str, [str], [str]) -> Page
        """Creates a new page in Confluence inside the space_key given,
        under the parent_page_id as a child page

        :param page_title: String with the title of the page
            that will be created
        :param space_key: String with the space key in confluence
            in which the page will exists.
        :param page_content: HTML String Content of the page
            that will be created
        :param parent_page_id: (optional) String with the ID number
            of the parent page in which the page will be created as a child page
        :param content_type: (optional) argument for content
            ('page' as default)
        :return: Page Content Object
        :rtype: Page
        """
        # json structure for a new page
        data = {
            'type': content_type,
            'title': page_title,
            'space': {
                'key': space_key
            },
            'body': {
                'storage': {
                    'value': page_content,
                    'representation': 'storage'
                }
            }
        }
        if parent_page_id:
            data['ancestors'] = [{
                'type': content_type,
                'id': parent_page_id
            }]

        response = self._post('content', {}, data)
        # create new page object from response gotten
        new_page = Page(response)
        return new_page

    def update_page(self,
                    page_id,
                    new_content,
                    new_title,
                    new_version,
                    new_parent=None,
                    edit_message=None
                    ):
        # type: (str, str, str, str, int, str) -> Page
        """Updates an existing page in Confluence with the given page ID.

        Properties that can be updated:
        - the content of the page
        - the title of the page
        - the version of the page
        - the parent of the page

        :param page_id: The confluence page unique ID.
        :param new_content: The new content to update in the page.
        :param new_title: The new title for the page
        :param new_version: This should be the current version + 1.
        :param new_parent: (optional) The new parent content unique id.
        :param edit_message: (optional) Edit message.
        :param expand: (optional) A list of properties to be expanded
                on the resulting content object.
        :rtype: Page
        """
        # json structure to update a confluence page
        data = {
            'type': 'page',
            'title': new_title,
            'body': {
                'storage': {
                    'value': new_content,
                    'representation': 'storage'
                }
            },
            'version': {
                'number': new_version
            }
        }

        if edit_message:
            data['version']['message'] = edit_message

        if new_parent:
            data['ancestors'] = [{
                'id': new_parent
            }]

        content_path = 'content/{}'.format(page_id)
        response = self._put(content_path, {}, data)
        # create new page object from response gotten
        new_page = Page(response)
        return new_page

    def delete_content(self, content_id, content_status='current'):
        # type: (str, [str]) -> None
        """Deletes the content in Confluence with the given ID

        :param content_id: String with the ID number of the content
            (ex. page id of confluence page)
        :param content_status: String with the status in which
            content will be deleted / purged
            values: 'current', 'trashed'
        :return: None
        """
        url_delete_content = 'content/{}'.format(content_id)
        #
        self._delete(
            path=url_delete_content,
            params={'status': content_status}
        )

    def get_content(self, content_id, content_status='current', expand=None):
        # type: (str, [str], [list]) -> Page
        """

        :param content_id: id number of the content to search for
            ex. page_id = 1291392
        :param content_status:
        :param expand:
        :return: Page instance
        """
        url_get_content = 'content/{}'.format(content_id)
        params = {'status': content_status}

        # when expand is None, default values should be used
        # in order to retrieve the default page content
        # body.storage contains the HTML content of the page
        if expand is None:
            expand = ['history', 'space', 'version', 'body.storage']
            # add expand on the request parameters
            params['expand'] = ','.join(expand)

        response = self._get(
            path=url_get_content,
            params=params
        )
        # Create Page Object with all data abstracted from request
        new_page = Page(response)
        return new_page

    def content_exists(self, content_id, content_status='current'):
        # type: (str, [str]) -> bool
        """

        :param content_id: id number of the content to search for
            ex. page_id = 1291392
        :param content_status:
        :param expand:
        :return: Page instance
        """
        url_get_content = 'content/{}'.format(content_id)
        content_exists = True

        try:
            # try to get the content. If no exception is thrown,
            # the content exists.
            self._get(
                path=url_get_content,
                params={'status': content_status}
            )
        except ConfluenceNotFoundError as ex:
            LOGGER.info("Content with ID '{content_id}' not found: {ex}".format(
                content_id=content_id,
                ex=ex))
            # Content does not exists
            content_exists = False
        return content_exists

    def page_exists(self, title, space):
        # type: (str, str) -> bool
        """Returns True if the page with the given title and space exists.
        Otherwise returns False.

        :param title: title of the confluence page to search
        :param space: space in which the confluence page is contained
        :return: bool
        """

        page_exists = True
        content_params = {
            'title': title,
            'spaceKey': space
        }
        try:
            json_response = self._get(
                path='content',
                params=content_params
            )
            # instance a page object from json API response
            # to validate that it exits. If not, an IndexError
            # exception will be thrown.
            Page(json_response)
        except ConfluenceNotFoundError as ex:
            LOGGER.info(
                "Page with title '{page_title}' "
                "not found in space key '{space_key}': {ex}".format(
                    page_title=title,
                    space_key=space,
                    ex=ex))
            # the content (page) does not exists
            page_exists = False
        except ConfluenceError as ex:
            # some other error happened
            raise ex
        except IndexError:
            # IndexError is thrown by Page object constructor
            # when it cannot be created due that API json results
            # array is empty. Meaning the page does not exist.
            page_exists = False
        return page_exists

    def get_page_from_title(self, page_title, space_key, expand=None):
        # type: (str, str, list) -> Page
        """Searches in confluence server for a page that correspond
        to the page title and space key given.

        If the page exists, a new Page instance will be created
        that will have and API to retrieve its content (like HTML)

        :param page_title: title of the page to look for
        :param space_key: space in which the page is located
        :param expand: API parameter to specify the data retrieved of the page
        :return: Page instance
        """
        params = {
            'title': page_title,
            'spaceKey': space_key
        }

        # when expand is None, default values should be used
        # in order to retrieve the default page content
        # body.storage contains the HTML content of the page
        if expand is None:
            expand = ['history', 'space', 'version', 'body.storage']
            # add expand on the request parameters
            params['expand'] = ','.join(expand)

        response = self._get(
            path='content',
            params=params
        )

        new_page = Page(response)
        return new_page


class Page(Content):
    """Class needed to abstract the content of an HTTP json response
    that should contain a Confluence Page which was retrieve from
    Confluence REST API.

    This abstraction will retrieve the metadata from json response and
    it will create properties into Page object mapped to those values.
    """

    def __init__(self, json_data):
        # type: (dict) -> Page
        super(Page, self).__init__(json_data)
        self._id_number = None
        self._title = None
        self._space_key = None
        self._content = None
        self._permanent_link = None
        self._base_url = None
        self._version = None
        self._retrieve_values_from_json()
        LOGGER.debug("New Page Object created: %s", self)

    def _retrieve_results_from_json(self):
        # type: () -> dict
        """Validates if json API response contains a dictionary with
        the results with Page data.

        :raises IndexError: in case 'results' is not found in api response
        :return: the json api response with the page data
        """
        # attributes model reference:
        # https://docs.atlassian.com/ConfluenceServer/rest/6.12.1/
        json_api_results = self.json_data_model
        # check if API response is contained inside
        # 'results' json object
        if 'results' in json_api_results.keys():
            # check if results contains any data
            # in order to retrieve values from it
            if json_api_results['results']:
                json_api_results = json_api_results['results'][0]
            else:
                raise IndexError("Page object cannot be instanced because "
                                 "API response 'results' is empty.")
        return json_api_results

    def _validate_links_section(self, json_data_response):
        # type: (dict) -> str
        """Validates and retrieves _links section data
        out of the api response in order to get links data
        """
        missing_value = None
        # links
        if '_links' in json_data_response.keys():
            # permanent link
            if 'tinyui' in json_data_response['_links'].keys():
                self._permanent_link = str(json_data_response['_links']['tinyui'])
            else:
                missing_value = '_links.tinyui'
        else:
            missing_value = '_links'
        return missing_value

    def _validate_body_section(self, json_data_response):
        # type: (dict) -> str
        """Validates and retrieves body section data
        out of the api response in order to get html content
        """
        missing_value = None
        # body.view.value (HTML Content)
        if 'body' in json_data_response.keys():
            if 'storage' in json_data_response['body'].keys():
                if 'value' in json_data_response['body']['storage'].keys():
                    self._content = str(json_data_response['body']['storage']['value'])
                else:
                    missing_value = 'body.storage.value'
            else:
                missing_value = 'body.storage'
        else:
            missing_value = 'body'
        return missing_value

    def _validate_metadata_section(self, json_data_response):
        # type: (dict) -> str
        """Validates and retrieves metadata section data
        out of the api response in order to get id, title and space
        """
        missing_value = None
        # id
        if 'id' in json_data_response.keys():
            self._id_number = str(json_data_response['id'])
        else:
            missing_value = 'id'
        # title
        if 'title' in json_data_response.keys():
            self._title = str(json_data_response['title'])
        else:
            missing_value = 'title'
        # space
        if 'space' in json_data_response.keys():
            # space key
            if 'key' in json_data_response['space'].keys():
                self._space_key = str(json_data_response['space']['key'])
            else:
                missing_value = 'space.key'
        else:
            missing_value = 'space'
        # version
        if 'version' in json_data_response.keys():
            # space key
            if 'number' in json_data_response['version'].keys():
                self._version = str(json_data_response['version']['number'])
            else:
                missing_value = 'version.number'
        else:
            missing_value = 'version'
        return missing_value

    def _retrieve_values_from_json(self):
        # type: () -> None
        """Retrieves the values from the HTTP response in json format
        that are important for the page object, like id, title,
        space, HTML content, web link.

        If some value is missing, an exception will be raised

        Then, it adds those values to the Page model
        into properties of the instance

        :return: None
        :raises Exception: if a value is not present on json model
        """

        # retrieve base url for the server host from response
        if '_links' in self.json_data_model.keys():
            if 'base' in self.json_data_model['_links'].keys():
                self._base_url = self.json_data_model['_links']['base']

        # retrieve results dictionary with Page data from json api response
        json_data_response = self._retrieve_results_from_json()

        # retrieve _links section from API response
        missing_value = self._validate_metadata_section(json_data_response)

        if missing_value is None:
            # retrieve _links section from API response
            missing_value = self._validate_links_section(json_data_response)

        if missing_value is None:
            # retrieve body section from API response
            missing_value = self._validate_body_section(json_data_response)

        if missing_value is not None:
            raise Exception("Page object cannot be instanced because "
                            "there is a missing value in json data: "
                            "\"{val}\"".format(val=missing_value))

    @property
    def id_number(self):
        # type: () -> str
        """Returns the id number of the Confluence page
        """
        return self._id_number

    @property
    def title(self):
        # type: () -> str
        """Returns the title of the Confluence page
        """
        return self._title

    @property
    def content(self):
        # type: () -> str
        """Returns the HTML content retrieved from Confluence page
        """
        return self._content

    @property
    def space_key(self):
        # type: () -> str
        """Returns the space kay name in which the Confluence page belongs to
        """
        return self._space_key

    @property
    def version(self):
        # type: () -> str
        """Returns the current version number for that Confluence page
        """
        return self._version

    @property
    def permanent_link(self):
        # type: () -> str
        """Returns the permanent link of the Confluence Page

        (this link will be always point to that page
        even if it changes it title or location)
        """
        return self._permanent_link

    @property
    def base_url(self):
        # type: () -> str
        """Returns the base url of the server host in which
        the API response was received
        """
        return self._base_url

    def get_page_url(self):
        # type: () -> str
        """Returns the permanent link of the Confluence Page

        (this link will be always point to that page
        even if it changes it title or location)
        """
        return self.base_url + self.permanent_link

    def __str__(self):
        # type: () -> str
        """Returns a string representation of the current Page instance
        with metadata like: Type, Id, Space, Title, Link, html content
        """
        status = "Confluence Content - " \
                 "ID: \"{id}\" - " \
                 "SPACE: \"{space}\" - " \
                 "TITLE: \"{title}\" - " \
                 "VERSION: \"{version}\" - " \
                 "PERMALINK: \"{permalink}\" - " \
                 "CONTENT: \"{content}\""
        if self.content is None:
            content_string = status.format(
                id=self.id_number,
                space=self.space_key,
                title=self.title,
                version=self.version,
                permalink=self.permanent_link,
                content="No Content"
            )
        else:
            content_string = status.format(
                id=self.id_number,
                space=self.space_key,
                title=self.title,
                version=self.version,
                permalink=self.permanent_link,
                content="Yes"
            )
        return content_string


class ContentError(Content):
    """Class needed to abstract the content of an HTTP json response
    that is an ERROR response from Confluence REST API.

    ex. when page does not exist
    """

    def __init__(self, json_data):
        # type: (dict) -> ContentError
        super(ContentError, self).__init__(json_data)
        self._message = None
        self._status_code = None
        self._retrieve_values_from_json()

    def _retrieve_values_from_json(self):
        """Retrieves the values from HTTP json response from REST API
        that are meaningful for Error Content (message and status code)

        :return: None
        :raises Exception: if a value is not present on json model
        """
        missing_value = None
        # message
        if 'message' in self.json_data_model.keys():
            self._message = self.json_data_model['message']
        else:
            missing_value = 'message'
        # statusCode
        if 'statusCode' in self.json_data_model.keys():
            self._status_code = self.json_data_model['statusCode']
        else:
            missing_value = 'statusCode'

        if missing_value is not None:
            raise Exception("ContentError object cannot be instance because "
                            "there is a missing value in json data: "
                            "\"{val}\"".format(val=missing_value))

    @property
    def message(self):
        """Returns the error message of the HTTP error response
        """
        return self._message

    @property
    def status_code(self):
        """Returns the status code of the HTTP error response
        """
        return self._status_code
