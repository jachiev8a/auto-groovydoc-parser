"""
Module with utilities needed to manage configuration files
"""
import collections

from confluence.models import json_model
from utilities.json_utils import JsonDataFile


class Config(object):
    """Class to manage the configuration for PageManager class
    in json format
    """

    MANDATORY_CONFIG_LIST = [
        # mandatory confluence settings
        json_model.JSON_ATTR_HOST_URL,          # confluence host URL (with port)
        json_model.JSON_ATTR_USER,              # user authentication in confluence
        json_model.JSON_ATTR_PASS,              # password authentication in confluence
        # mandatory template settings
        json_model.JSON_ATTR_SOURCE,            # html template source: URL or file path
        # mandatory confluence page settings
        json_model.JSON_ATTR_SPACE_KEY,         # space in which page will be generated
        json_model.JSON_ATTR_PARENT_PAGE_ID,    # id of the parent page container
        json_model.JSON_ATTR_PAGE_TITLE         # title of the page to be generated
    ]

    def __init__(self, json_file):
        # type: (str) -> None
        """Constructor method

        :param json_file: path to the json config file
        """
        self._json_data_obj = JsonDataFile(json_file)
        self._template_variables = collections.OrderedDict()
        # validate config file structure and variables
        self._validate_mandatory_configuration()
        self._validate_template_variables()

    @property
    def template_variables(self):
        # type: () -> dict
        """Returns a dictionary with the template variables
        $VarName = value

        :return: a dictionary with the template variables
        """
        return self._template_variables

    def _validate_mandatory_configuration(self):
        # type: () -> None
        """Validates that json file has the mandatory values needed
        for the configuration, if one is not configured, an exception
        will be raised.

        :return: None.
        :raises AttributeError:
            if mandatory configuration attribute is not configured
        """
        for config_attr in Config.MANDATORY_CONFIG_LIST:
            if not self._json_data_obj.has_json_attribute(config_attr):
                raise AttributeError(
                    "configuration file does not contain mandatory "
                    "attribute \"{attr}\". Please be sure to add it and "
                    "configure it in: \"{config_file}\"".format(
                        attr=config_attr,
                        config_file=self._json_data_obj.file_name))

    def _validate_template_variables(self):
        # type: () -> None
        """Searches on the json configuration if there are variables
        starting with '$' character and it loads them into the template
        variable dictionary from the instance to be available as an interface

        :return: None.
        """
        for var_name, var_value in self._json_data_obj.json_model_dict.items():
            if var_name.startswith('$'):
                self._template_variables[var_name] = var_value

    def get_host_url(self):
        # type: () -> str
        """Returns the value of the host configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_HOST_URL
        )

    def get_user(self):
        # type: () -> str
        """Returns the value of the user configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_USER
        )

    def get_password(self):
        # type: () -> str
        """Returns the value of the password configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_PASS
        )

    def get_space_key(self):
        # type: () -> str
        """Returns the value of the confluence space configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_SPACE_KEY
        )

    def get_parent_page_id(self):
        # type: () -> str
        """Returns the value of the parent page id number configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_PARENT_PAGE_ID
        )

    def get_page_title(self):
        # type: () -> str
        """Returns the value of the title of the confluence page
        configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_PAGE_TITLE
        )

    def get_source(self):
        # type: () -> str
        """Returns the value of the template source configured on the json file
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_model.JSON_ATTR_SOURCE
        )

    def get_value_from_json_variable(self, json_variable_name):
        # type: (str) -> str
        """Checks if json file has the json variable given inside its content
        and returns the value of it

        :param json_variable_name:
        :return:
        """
        return self._json_data_obj.get_value_from_json_ref(
            json_variable_name
        )
