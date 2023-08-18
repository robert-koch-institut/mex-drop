.PHONY: all test setup hooks install linter pytest build docker start
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
	# run the poetry installation with embedded virtual environment
	@ echo installing package; \
	poetry install --no-interaction --sync; \

linter:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

pytest:
	# run the pytest test suite
	@ echo running tests; \
	poetry run pytest -m "not integration"; \

build:
	# build the python package
	@ echo building wheel; \
	poetry build --no-interaction --format wheel; \

docker:
	# build the docker image
	@ echo building docker image mex-drop:${LATEST}; \
	docker build \
		--build-arg="GIT_REV=${LATEST}" \
		--tag rki/mex-drop:${LATEST} \
		--tag rki/mex-drop:latest .; \

start: docker
	# start the docker image
	@ echo running docker image mex-drop:${LATEST}; \
	docker run \
		--publish 8081:8081 \
		rki/mex-drop:${LATEST}; \
