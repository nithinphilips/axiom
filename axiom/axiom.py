# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

"""axiom.axiom: provides entry point main()."""


__version__ = "0.1.0"

import argcomplete
import argparse
import logging
import sys

from argh import ArghParser, completion, arg

from .stuff import Stuff

# These arguments are used by this global dispatcher and each individual
# stand-alone commands.
COMMON_PARSER = argparse.ArgumentParser(add_help=False)
COMMON_PARSER.add_argument('--debug',
                           action='store_true',
                           default=False,
                           help="Enable debug logging.")

def main():
    parser = ArghParser(parents=[COMMON_PARSER])
    parser.add_commands(
        [
            ting
        ]
    )
    completion.autocomplete(parser)

    # Parse ahead
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    parser.dispatch()

# adding help to `foo` which is in the function signature:
@arg('foo', help='blah')
# these are not in the signature so they go to **kwargs:
@arg('baz')
@arg('-q', '--quux')
# the function itself:
def ting(foo, bar=1, *args, **kwargs):
    logging.info("You turned on --debug")
    yield foo
    yield bar
    yield ', '.join(args)
    yield kwargs['baz']
    yield kwargs['quux']

class Boo(Stuff):
    pass
