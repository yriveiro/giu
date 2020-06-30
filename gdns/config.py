from pathlib import Path

from tomlkit.toml_document import TOMLDocument
from tomlkit.toml_file import TOMLFile


class ConfigError(Exception):
    """Config Exception."""

    pass


def parse(config_file: Path) -> TOMLDocument:
    """Parse configuration file
    Args:
        config_file (Path): Path of the configuration file.

    Returns:
        TOMLDocument with the content of the file parsed.

    Raises:
        RuntimeError if the file is not found.
        ConfigError if tomlkit fails to parse the file."""
    path = Path(config_file)

    if not path.exists():
        raise RuntimeError(f'Configuration file {config_file} not found.')

    try:
        return TOMLFile(path).read()
    except Exception as exc:
        raise ConfigError(f'Failed to parse {config_file}') from exc
