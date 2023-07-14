# MEx drop

Data upload API for the MEx project.

## project

With the Metadata Exchange (MEx) project, the [RKI](https://www.rki.de) is developing a
transparency platform for finding metadata on the institute's research activities and
data.

MEx makes metadata findable, accessible, and shareable on a daily basis,
as well as available for further research. MEx enables users to get an overview of what
research data is available, understand its context, and know what needs to be considered
for subsequent use.

The platform is currently in internal use but will also be made publicly available
and thus be available to external researchers as well as the interested (professional)
public.

For further details, please consult the
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

## package

The `mex-drop` package provides an API for uploading data to the MEx project.

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
- commit udpate `git commit --message "..." pyproject.toml`
- create a tag `git tag ...`
- push `git push --follow-tags`
