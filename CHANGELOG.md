# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

- update mex-common to 0.52.2
- use a model for file-history state
- show an empty file-history page even when x-system is not found
- clean up styling a bit

### Deprecated

### Removed

### Fixed

### Security

## [0.10.0] - 2025-02-19

### Changes

- update mex-common to version 0.49.3
- BREAKING: you must start the local dev mode simply with `pdm run drop` (no 2nd run)
- move custom backend exception handler to its own module
- move custom api code to its own package `mex.drop.api`
- align general layout functions (page, logo, navbar, etc) with mex-editor
- align login component and navbar state handling with mex-editor
- update styling with more idiomatic variable syntax and responsive scaling

### Fixed

- decorate state handlers with `@rx.event` to satisfy new reflex versions

## [0.9.1] - 2025-01-09

### Added

- mex-drop UI shows file list with name and timestamps

## [0.9.0] - 2024-12-05

### Added

- add entrypoint for starting only the api: `backend-only`

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
