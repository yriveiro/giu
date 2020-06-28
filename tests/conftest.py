from pathlib import Path

import pytest


@pytest.fixture()
def fixture_dir():
    def _fixture_dir(name):
        return Path(__file__).parent / 'fixtures' / name

    return _fixture_dir
