#!/usr/bin/env python
# coding=utf-8
"""
Main script to ...
"""

# get common libraries
import argparse
import collections
import logging
import os
import sys
import re

from confluence import confluence_api
from utils.parser import GroovyDocParser

LOGGER = logging.getLogger()


def configure_logger(global_logger, log_level):
    # type: (logging.Logger, str) -> None
    """Configures the main common object.
    log level is set for logging level.

    :param global_logger: main common instance
    :param log_level:
        logging level [ error > warning > info > debug > off ]
    :return:
    """
    log_levels = {
        'off': logging.NOTSET,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    if log_level not in log_levels.keys():
        raise ValueError("Logging level not valid: '{}'".format(log_level))
    else:
        log_level = log_levels[log_level]
    global_logger.setLevel(logging.DEBUG)
    # script file reference
    this_script_file_name = os.path.basename(__file__)
    scripts_log_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'logs'))
    # logs directory
    if not os.path.exists(scripts_log_dir):
        os.mkdir(scripts_log_dir)
    # logs file for this script
    log_file_basename = "{}.log".format(os.path.splitext(this_script_file_name)[0])
    log_file_path = os.path.normpath(os.path.join(scripts_log_dir, log_file_basename))
    # create file handler which logs even debug messages
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(log_level)
    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        fmt='%(asctime)s :%(module)-20s: [%(levelname)s] -> %(message)s',
        datefmt='%Y-%m-%d,%H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # add the handlers to the common
    global_logger.addHandler(file_handler)
    global_logger.addHandler(console_handler)


# -----------------------------------
# MAIN
# -----------------------------------
def main():
    """Main Function
    """

    this_script_name = os.path.basename(__file__)

    # Script Argument Parser
    parser = argparse.ArgumentParser(description=this_script_name)
    # parser.add_argument(
    #     '-u', '--user',
    #     default=None,
    #     required=True,
    #     help='user to be used to authenticate to the Confluence API. '
    #          'This will be used if it is not configured in json file')
    # parser.add_argument(
    #     '-p', '--password',
    #     default=None,
    #     required=True,
    #     help='password for the user used to authenticate to the Helix Swarm API. '
    #          'This will be used if it is not configured in json file')
    # parser.add_argument(
    #     '-U', '--confluence-url',
    #     required=True,
    #     help='Confluence base URL. (Ex. http://confluence-host.net)')
    # parser.add_argument(
    #     '-P', '--page',
    #     required=True,
    #     help='Helix Swarm review number. (Ex. 10233)')
    # parser.add_argument(
    #     '-o', '--output-only',
    #     action='store_true',
    #     required=False,
    #     help='if this flag is set, script will only print to STDOUT the data output expected'
    #          '(Ex. -d email / -d username)')
    # parser.add_argument(
    #     '-l', '--log-level',
    #     default="warning",
    #     required=False,
    #     help='debugging script log level '
    #          '[ critical > error > warning > info > debug > off ]')
    # args = parser.parse_args()

    # parser.add_argument(
    #     '-c', '--config_file',
    #     required=True,
    #     help='Script configuration file (JSON Format)')
    # parser.add_argument(
    #     '-u', '--user',
    #     default=None,
    #     required=False,
    #     help='user to be used to authenticate to the Confluence API. '
    #          'This will be used if it is not configured in json file')
    # parser.add_argument(
    #     '-p', '--password',
    #     default=None,
    #     required=False,
    #     help='password for the user used to authenticate to the Confluence API. '
    #          'This will be used if it is not configured in json file')
    # parser.add_argument(
    #     '-o', '--overwrite',
    #     action='store_true',
    #     required=False,
    #     help='If set, this will overwrite the content of the page'
    #          'if the configured page is an existing one.')
    # parser.add_argument(
    #     '-l', '--log_level',
    #     default="warning",
    #     required=False,
    #     help='debugging script log level '
    #          '[ error > warning > info > debug > off ]')

    #args = parser.parse_args()

    # script here
    # -------------------------------------------------------------------
    # Create a confluence page manager instance that
    # will read & validate all values from config file.
    # This manager object will work as an API
    # to create, delete, retrieve confluence pages.
    confluence_api_obj = confluence_api.ConfluenceApi(
        'https://confluence-oc.osramcontinental.net/',
        'ocg00007',
        'J3nk1nsAme.'
    )

    template_page = confluence_api_obj.get_content('55900721')
    template_raw_content = template_page.content
    base_formatted_content = ''

    re_function_section = re.compile(r'\${groovy.function_block.open}(.*)\${groovy.function_block.close}')
    template_function_section = re.findall(re_function_section, template_raw_content)
    template_function_section = template_function_section[0]

    base_formatted_content = template_function_section
    formatted_groovy_functions = []

    parsed_groovy_obj = GroovyDocParser.parse_file('D:/pipeline-utils-jenkins.groovy')
    for function_obj in parsed_groovy_obj.get_groovy_functions().values():
        current_function_format = ''
        current_function_format = base_formatted_content.replace(
            '${groovy.title}',
            function_obj.name
        )

        current_function_format = current_function_format.replace(
            '${groovy.header}',
            function_obj.header
        )

        current_function_format = current_function_format.replace(
            '${groovy.description}',
            function_obj.description_confluence_format()
        )

        # parameters section
        function_parameter_section = ''
        function_parameter_section += '<ul>\n'
        for parameter_obj in function_obj.parameters.values():
            function_parameter_section += '<li>\n'
            function_parameter_section += parameter_obj.confluence_format()
            function_parameter_section += '</li>\n'
        function_parameter_section += '</ul>\n'

        current_function_format = current_function_format.replace(
            '${groovy.parameters}',
            function_parameter_section
        )

        current_function_format = current_function_format.replace(
            '${groovy.returns}',
            function_obj.returns
        )

        current_function_format = current_function_format.replace(
            '${groovy.function_code}',
            function_obj.code_definition
        )
        formatted_groovy_functions.append(current_function_format)

    final_content_page = ''
    for formatted_function in formatted_groovy_functions:
        final_content_page += formatted_function

    target_page = confluence_api_obj.get_content('55900864')
    target_page_raw_content = target_page.content
    target_page_final_content = target_page_raw_content.replace(
        '${groovy.target}',
        final_content_page
    )

    new_version = str(int(target_page.version) + 1)

    confluence_api_obj.update_page(
        '55900864',
        target_page_final_content,
        'TemplateTarget',
        new_version
    )

    LOGGER.info("[{script}] Finish [OK]".format(script=this_script_name))


if __name__ == "__main__":
    main()
