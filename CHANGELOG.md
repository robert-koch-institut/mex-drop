# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

- update mex-common, mex-template and pinned dependencies

### Deprecated

### Removed

### Fixed

### Security

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
