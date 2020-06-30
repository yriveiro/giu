from unittest import mock

import pytest
import requests_mock
from gdns.config import parse
from gdns.resolver import Resolver
from gdns.resolver import ResolverError
from halo import Halo
from requests import Timeout


def test_resolve_empty_provider_list(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    config['resolver']['providers'] = []

    with pytest.raises(ResolverError, match=r'^the list of providers .*'):
        Resolver(config['resolver']['providers'], Halo())


def test_resolve(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    resolver = Resolver(config['resolver']['providers'], Halo())

    assert type(resolver) == Resolver


def test_resolve_ip(fixture_dir):
    with mock.patch.object(Resolver, 'ip', '127.0.0.1'):
        config = parse(fixture_dir('config.toml'))
        resolver = Resolver(config['resolver']['providers'], Halo())

        assert resolver.ip == '127.0.0.1'


def test_resolve_ip_request_mock(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    resolver = Resolver(config['resolver']['providers'], Halo())

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri('GET', 'https://ifconfig.me/ip', text='127.0.0.1')

        assert resolver.ip == '127.0.0.1'


def test_resolve_no_providers(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    resolver = Resolver(config['resolver']['providers'], Halo())
    resolver._providers = []

    with pytest.raises(ResolverError):
        resolver.ip


def test_resolve_wrong_ip(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    resolver = Resolver(config['resolver']['providers'], Halo())

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri('GET', 'https://ifconfig.me/ip', text='not valid ip')

        with pytest.raises(ResolverError, match='all provider failed or timeout'):
            resolver.ip


def test_resolve_ip_timeout(fixture_dir):
    config = parse(fixture_dir('config.toml'))
    resolver = Resolver(config['resolver']['providers'], Halo())

    with requests_mock.Mocker(real_http=True) as m:
        m.register_uri('GET', 'https://ifconfig.me/ip', exc=Timeout)

        with pytest.raises(ResolverError, match='all provider failed or timeout'):
            resolver.ip
