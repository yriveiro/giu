import pytest
from gdns.config import ConfigError
from gdns.config import parse
from tomlkit.items import Table


def test_config(fixture_dir):
    config = parse(fixture_dir('config.toml'))

    assert 'dns' in config
    assert 'api' in config
    assert type(config['api']) == Table
    assert config['api']['url'] == 'https://dns.api.gandi.net/api/v5'


def test_config_path_not_exists(fixture_dir):
    with pytest.raises(RuntimeError, match=r'^Configuration file .*'):
        parse(fixture_dir('foo.toml'))


def test_config_invalid_toml_syntax(fixture_dir):
    with pytest.raises(ConfigError, match=r'^Failed to parse .*'):
        parse(fixture_dir('invalid.toml'))
