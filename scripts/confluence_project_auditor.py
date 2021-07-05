#!/usr/bin/env python
# coding=utf-8
"""
Main script to...
"""

import argparse
import logging
import os
from confluence import confluence_api

# get logger instance
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
    formatter = logging.Formatter('%(asctime)s :%(name)-24s: [%(levelname)s] -> %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # add the handlers to the common
    global_logger.addHandler(file_handler)
    global_logger.addHandler(console_handler)


# ---------------
# MAIN
# ---------------
def main():
    """Main Function
    """

    # Script Argument Parser
    parser = argparse.ArgumentParser(description='confluence_project_auditor.py')
    parser.add_argument(
        '-u', '--user',
        default=None,
        required=True,
        help='user to be used to authenticate to the Confluence API. '
             'This will be used if it is not configured in json file')
    parser.add_argument(
        '-p', '--password',
        default=None,
        required=True,
        help='password for the user used to authenticate to the Helix Swarm API. '
             'This will be used if it is not configured in json file')
    parser.add_argument(
        '-U', '--confluence-url',
        required=True,
        help='Confluence base URL. (Ex. http://confluence-host.net)')
    parser.add_argument(
        '-P', '--page',
        required=True,
        help='Helix Swarm review number. (Ex. 10233)')
    parser.add_argument(
        '-o', '--output-only',
        action='store_true',
        required=False,
        help='if this flag is set, script will only print to STDOUT the data output expected' 
             '(Ex. -d email / -d username)')
    parser.add_argument(
        '-l', '--log-level',
        default="warning",
        required=False,
        help='debugging script log level '
             '[ critical > error > warning > info > debug > off ]')
    args = parser.parse_args()

    if args.output_only:
        # turn off the logger. Not needed
        configure_logger(LOGGER, 'critical')
    else:
        # configure logging properties with configuration given
        configure_logger(LOGGER, args.log_level)

    # Create a Confluence API object to interact with server API
    confluence_api_obj = confluence_api.ConfluenceApi(
        args.confluence_url,
        args.user,
        args.password
    )

    page = confluence_api_obj.get_content(args.page)
    

if __name__ == "__main__":
    main()
