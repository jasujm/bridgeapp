"""
Bridgeapp command line interface
--------------------------------

The command line interface has tools for managing an installation.
"""

import logging

import click
import click_log

from . import db, search

click_log.basic_config()
logger = logging.getLogger(__name__)


@click.group()
@click_log.simple_verbosity_option()
def cli():
    """Bridgeapp command line interface"""


@cli.command()
def init():
    """Create database tables and search indices"""
    db.init()
    search.init()


cli()
