# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""axiom.axiom: provides entry point main()."""


__version__ = "0.2.0"

import argcomplete
import argparse
import logging
import sys

from argh import ArghParser, completion, arg

from .pmschedulevalidator import schedulevalidator
from .pmeventparser import eventparser

# These arguments are used by this global dispatcher and each individual
# stand-alone commands.
COMMON_PARSER = argparse.ArgumentParser(add_help=False)
COMMON_PARSER.add_argument('--debug',
                           action='store_true',
                           default=False,
                           help="Enable debug logging.")

def schedulevalidator_entry():
    parser = ArghParser(parents=[COMMON_PARSER])
    parser.set_default_command(schedulevalidator)
    completion.autocomplete(parser)

    # Parse ahead
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    parser.dispatch()

def eventparser_entry():
    parser = ArghParser(parents=[COMMON_PARSER])
    parser.set_default_command(eventparser)
    completion.autocomplete(parser)

    # Parse ahead
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    parser.dispatch()

