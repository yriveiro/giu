from pathlib import Path
from typing import Dict

import click
from halo import Halo

from .config import parse
from .livedns import LiveDNS
from .livedns import LiveDNSException
from .resolver import Resolver
from .resolver import ResolverError

spinner = Halo(text='Loading', spinner='dots')


@click.group()
@click.pass_context
def giu(ctx: Dict) -> None:
    """Commnand line tool to interact with Gandi LiveDN."""


@giu.command()
@click.pass_context
@click.option('--config', default='config.toml', help='Path to the config file.')
@click.option('--dry-run', is_flag=True, help='Dry run mode on.')
@click.option('--debug', is_flag=True, help='Dry run mode on.')
def sync(ctx: click.core.Context, config: Path, dry_run: bool, debug: bool) -> None:
    """Sync you dynamic ip to the 'A' record on Gandi LiveDNS"""

    try:
        conf = parse(config)

        if not conf:
            raise RuntimeError('parse config operation failed')

        spinner.start('Feching dynamic IP assigned')

        ip = Resolver(conf['resolver']['providers'], spinner).ip

        if not ip:
            raise RuntimeError('unable to resolve current assigned ip')

        spinner.succeed('Dynamic IP fetched.')
        spinner.info(f'Current dynamic IP: {ip}')

        if ctx.params['dry_run']:
            spinner.info('Dry run mode on.')

        dns = LiveDNS(conf['api']['url'], conf['api']['key'], spinner, **ctx.params)
        dns.sync(ip, conf['dns']['domain'], conf['dns']['records'])
    except (RuntimeError, LiveDNSException, ResolverError) as exc:
        raise RuntimeError('sync command failed') from exc
    finally:
        spinner.stop()
