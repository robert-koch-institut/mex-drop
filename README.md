# MEx drop

Data upload API for the MEx project.

[![testing](https://github.com/robert-koch-institut/mex-drop/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-drop/actions/workflows/testing.yml)
[![linting](https://github.com/robert-koch-institut/mex-drop/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-drop/actions/workflows/linting.yml)
[![cve-scan](https://github.com/robert-koch-institut/mex-drop/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-drop/actions/workflows/cve-scan.yml)

## project


The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

## package

The `mex-drop` package provides an API for uploading data to the MEx project.
Request payloads need to be JSON-formatted but can have arbitrary structures.
Accepted data will be ingested and processed asynchronously.

## commands

- run `poetry run {command} --help` to print instructions
- run `poetry run {command} --debug` for interactive debugging

### mex drop

- `drop` starts the drop server
- `token` generate a cryptographically sound token

## development

### installation

- on unix, consider using pyenv https://github.com/pyenv/pyenv
  - get pyenv `curl https://pyenv.run | bash`
  - install 3.11 `pyenv install 3.11`
  - create env `pyenv virtualenv 3.11 mex`
  - go to repo root
  - use env `pyenv local mex`
  - run `make install`
- on windows, see https://python-poetry.org/docs/managing-environments
  - install `python3.11` in your preferred way
  - go to repo root
  - run `.\mex.bat install`

### linting and testing

- on unix run `make test`
- on windows run `.\mex.bat test`
- or run manually
  - linter checks via `pre-commit run --all-files`
  - all tests via `poetry run pytest`
  - just unit tests via `poetry run pytest -m "not integration"`

### updating dependencies

- update global dependencies in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update git hook additional dependencies manually
- show outdated dependencies with `poetry show --outdated`
- update dependencies in poetry using `poetry update --lock`
- update github actions manually in `.github/workflows/default.yml`

### creating release

- update version, eg `poetry version minor`
- commit update `git commit --message "..." pyproject.toml`
- create a tag `git tag ...`
- push `git push --follow-tags`

### container workflow

- build container with `make container`
- run directly using docker `make run`
- start with docker-compose `make start`
