# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- add entrypoint for starting only the api: `backend-only`

### Changes

### Deprecated

### Removed

### Fixed

### Security

## [0.8.0] - 2024-12-03

### Added

- mini UI for mex-drop users
- log in feature for mex-drop UI users

### Fixed

- fix docker image and run target in Makefile

## [0.7.0] - 2024-10-07

### Added

- support for structured file formats (xml, tsv, xls and xlsx)

### Fixed

- github action for containerization

## [0.6.0] - 2024-09-11

### Added

- created placeholder for the mex-drop UI with reflex stack
- configured firefox integration tests with playwright

### Changes

- updated project files to work with the reflex tech stack
- **BREAKING** move endpoint implementations from `main` to `api`

### Removed

- removed uvicorn entrypoint and logging config
- helm chart

## [0.5.0] - 2024-08-07

### Added

- multipart file upload support

### Changes

- update mex-common to 0.33.0

## [0.4.1] - 2024-07-17

### Changes

- update mex-common to 0.30.0

### Removed

- helm chart: container registry authentication

## [0.4.0] - 2024-06-14

### Changes

- update mex-common, mex-template and pinned dependencies

## [0.3.0] - 2024-03-22

### Added

- pull request template
- sphinx documentation
- pre-commit yaml check
- CHANGELOG file
- cruft template link
- open-code workflow
- add helm charts for k8s deployments
- endpoint for listing available x-systems (requires authentication for x-system `admin`)
- endpoint for listing downloadable files for an x-system
- endpoint for downloading data
- switch from poetry to pdm

### Changes

- harmonized boilerplate
- updated dependencies
- **BREAKING** rename setting `MEX_DROP_USER_DATABASE` to `MEX_DROP_API_KEY_DATABASE`

### Removed

- **BREAKING** remove the upload html form at `/v0/{x_system}/{entity_type}`,
  because the endpoint conflicted with the most obvious route for downloading files
