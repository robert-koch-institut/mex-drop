.PHONY: all test setup hooks install linter pytest wheel container run start docs
all: install test
test: linter pytest

LATEST = $(shell git describe --tags $(shell git rev-list --tags --max-count=1))

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	python -m pip --quiet --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	pdm sync --clean --group dev; \

linter:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

pytest:
	# run the pytest test suite with all unit tests
	@ echo running unit tests; \
	pdm run pytest -m "not integration"; \

wheel:
	# build the python package
	@ echo building wheel; \
	pdm build --no-sdist; \

container:
	# build the docker image
	@ echo building docker image mex-drop:${LATEST}; \
	export DOCKER_BUILDKIT=1; \
	docker build \
		--tag rki/mex-drop:${LATEST} \
		--tag rki/mex-drop:latest .; \

run: container
	# run the service as a docker container
	@ echo running docker container mex-drop:${LATEST}; \
	docker run \
		--env MEX_DROP_HOST=0.0.0.0 \
		--publish 8081:8081 \
		rki/mex-drop:${LATEST}; \

start: container
	# start the service using docker-compose
	@ echo running docker-compose with mex-drop:${LATEST}; \
	export DOCKER_BUILDKIT=1; \
	export COMPOSE_DOCKER_CLI_BUILD=1; \
	docker-compose up; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating api docs; \
	pdm run sphinx-apidoc -f -o docs/source mex; \
	pdm run sphinx-build -aE -b dirhtml docs docs/dist; \
