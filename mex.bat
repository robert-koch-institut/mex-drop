@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="test" goto test
echo invalid argument %target%
exit /b 1


:install
@REM install meta requirements system-wide
Python -m pip --quiet --disable-pip-version-check install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install pre-commit hooks when not in CI
if "%CI%"=="" (
    pre-commit install
    if %errorlevel% neq 0 exit /b %errorlevel%
)

@REM run the poetry installation with embedded virtual environment
echo installing packages
poetry install --no-interaction --sync
exit /b %errorlevel%


:test
@REM run the linter hooks from pre-commit on all files
echo linting all files
pre-commit run --all-files
if %errorlevel% neq 0 exit /b %errorlevel%

@REM run the pytest test suite with unit and optional integration tests
@REM whether integration tests are run as well is determined by pytest fixture
echo running test suite
poetry run pytest
exit /b %errorlevel%
