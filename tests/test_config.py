import pytest
from atoml.items import Table

from giu.config import ConfigError
from giu.config import parse


def test_config(fixture_dir):
    config = parse(fixture_dir('config.toml'))

    assert 'dns' in config
    assert 'api' in config
    assert type(config['api']) == Table
    assert config.get('api').get('url') == 'https://api.gandi.net/v5/livedns'


def test_config_path_not_exists(fixture_dir):
    with pytest.raises(RuntimeError, match=r'^Configuration file .*'):
        parse(fixture_dir('foo.toml'))


def test_config_invalid_toml_syntax(fixture_dir):
    with pytest.raises(ConfigError, match=r'^Failed to parse .*'):
        parse(fixture_dir('invalid.toml'))
