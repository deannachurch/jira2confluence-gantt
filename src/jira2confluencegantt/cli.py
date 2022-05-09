#! python3

"""
Main entry point to generate gantt chart
"""

import argparse
import logging
import subprocess
import sys
from .config import load_config
from .confluenceclient import ConfluenceClient
from .jiraclient import JiraClient
from .report import generate_all_reports

class LoadFromFile (argparse.Action):
    def __call__ (self, parser, namespace, values, option_string=None):
        with values as f:
            # parse arguments in the file and store them in the target namespace
            parser.parse_args(f.read().split(), namespace)

#def _input_password() -> str:
#    """
#    Get password input by masking characters.
#    Similar to getpass() but works with cygwin.
#    """
#    sys.stdout.write("Password :\n")
#    sys.stdout.flush()
#    subprocess.check_call(["stty", "-echo"])
#    password = input()
#    subprocess.check_call(["stty", "echo"])
#    return password


def _create_argument_parser() -> argparse.ArgumentParser:
    """
    Create the list of arguments supported and return the parser.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode",
        dest="verbose",
    )
    parser.add_argument(
        "config",
        action="store",
        help="Configuration file",
        nargs="?",
        metavar="config.yaml",
    )
    parser.add_argument(
        "--user",
        action="store",
        help="Define the user to connect to Atlassian server",
        dest="atlassian_user",
    )
    parser.add_argument(
        "--api_key",
        type=open,
        action=LoadFromFile,
        help="Define the api_key file to connect to Atlassian server",
        dest="atlassian_api",
    )
    return parser


def main() -> None:
    """
    Entry point of gantt generator script.
    """
    # Parse command line
    parser = _create_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Create logger
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=log_level,
    )

    if not args.config:
        parser.print_usage()
        return

    if args.atlassian_user is None:
        args.atlassian_user = str(input("Enter login for Atlassian :\n"))
    if args.atlassian_api is None:
        args.atlassian_api = str(input("Enter file with api key"))

    # Get configuration from JSON/YAML file
    config = load_config(args.config)
    if args.verbose:
        config.dump()

    jira_client = JiraClient(
        config.jira,
        args.atlassian_user,
        args.atlassian_api,
    )
    confluence_client = None
    if config.confluence:
        confluence_client = ConfluenceClient(
            config.confluence,
            args.atlassian_user,
            args.atlassian_api,
        )
    generate_all_reports(jira_client, config, confluence_client)
