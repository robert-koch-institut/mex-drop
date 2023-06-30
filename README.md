# MEx drop

Data upload API for the MEx project.

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

## commands

- run `poetry run {command} --help` to print instructions
- run `poetry run {command} --debug` for interactive debugging

### mex drop

- `drop` starts the drop server
