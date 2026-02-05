.PHONY: all setup hooks install lint unit test wheel image run start docs
all: install lint test

LATEST = $(shell git describe --tags $(shell git rev-list --tags --max-count=1))
PWD = $(shell pwd)

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	pip --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	uv sync; \
	# use playwright to install firefox
	@echo installing firefox; \
	uv run playwright install firefox; \

lint:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

unit:
	# run the test suite with all unit tests
	@ echo running unit tests; \
	uv run pytest -m 'not integration'; \

test:
	# run the unit and integration test suites
	@ echo running all tests; \
	uv run pytest; \

wheel:
	# build the python package
	@ echo building wheel; \
	uv build --wheel; \

image:
	# build the docker image
	@ echo building docker image mex-drop:${LATEST}; \
	docker build \
		--tag rki/mex-drop:${LATEST} \
		--tag rki/mex-drop:latest .; \

run: image
	# run the service as a docker container
	@ echo running docker container mex-drop:${LATEST}; \
	mkdir --parents --mode 777 $(PWD)/data; \
	docker run \
		--env MEX_DROP_DIRECTORY=data \
		--env MEX_DROP_API_HOST=0.0.0.0 \
		--env MEX_DROP_USER_DATABASE='{"mex":["mex"]}' \
		--publish 8020:8020 \
		--publish 8021:8021 \
		rki/mex-drop:${LATEST}; \

start:
	# start the service using docker compose
	@ echo start mex-drop:${LATEST} with compose; \
	docker compose up --remove-orphans; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating docs; \
	uv run sphinx-apidoc -f -o docs/source mex; \
	uv run sphinx-build -aE -b dirhtml docs docs/dist; \
