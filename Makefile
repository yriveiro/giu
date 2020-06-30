clean:
	$(info Cleaning up)
	@rm -rf build dist .eggs *.egg-info
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

coverage: clean
	@poetry run pytest -s --cov=gdns --cov-config .coveragerc --cov-report=html tests/

test:
	@poetry run pytest -s --cov=gdns --cov-config .coveragerc tests/

build: clean
	@poetry build

publish:
	@poetry publish

wheel: clean
	@poetry build -v

install:
	@poetry install

# run tests against all supported python versions
tox:
	@tox
