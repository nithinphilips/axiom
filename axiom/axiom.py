# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""axiom.axiom: provides entry point main()."""


__version__ = "0.2.2"

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
COMMON_PARSER.add_argument('--version',
                           action='store_true',
                           default=False,
                           help="Print version information and quit.")

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

    if args.version:
        print_version()
        return

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

    if args.version:
        print_version()
        return

    parser.dispatch()

def print_version():
    sys.stdout.write(
            "Axiom. Tool to validate TRIRIGA PM Schedules.\n"
            "Version {}\n"
            "\n"
            "Copyright (C) 2016 Nithin Philips\n"
            "\n"
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.\n"
            "\n"
            "This program is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
            "GNU General Public License for more details.\n"
            "\n"
            "You should have received a copy of the GNU General Public License\n"
            "along with this program.  If not, see <http://www.gnu.org/licenses/>.\n".format(__version__)
    )
