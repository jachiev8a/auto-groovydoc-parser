#!/usr/bin/env python
# coding=utf-8
"""
Main script to ...
"""

# get common libraries
import argparse
import logging
import os
import sys

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
    parser.add_argument(
        '-f', '--file',
        default=None,
        required=True,
        help='string file argument')
    parser.add_argument(
        '-v1', '--var1',
        default=None,
        required=True,
        help='string var')
    parser.add_argument(
        '-v2', '--var2',
        default=None,
        required=False,
        help='string var')
    parser.add_argument(
        '-d', '--flag',
        required=False,
        action="store_true",
        help='flag example')
    parser.add_argument(
        '-l', '--log-level',
        default="warning",
        required=False,
        help='debugging script log level '
             '[ critical > error > warning > info > debug > off ]')
    args = parser.parse_args()

    configure_logger(LOGGER, 'info')

    # script here
    # -------------------------------------------------------------------

    LOGGER.info("[{script}] Finish [OK]".format(script=this_script_name))


if __name__ == "__main__":
    main()
