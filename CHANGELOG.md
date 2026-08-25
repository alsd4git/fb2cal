# Changelog

All notable changes to this fork are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the maintained fork uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-08-19

### Added

- Cookie-based Facebook contact retrieval with offline test coverage.
- Structured birthday exports, recap output, and vCard generation.
- Reproducible packaging and dependency management with uv.
- Tagged GitHub releases containing validated wheel and source distributions.

### Changed

- Reworked authentication around the supported cookie workflow.
- Split Facebook session, login, calendar, and export responsibilities.
- Updated calendar and vCard output for standards compatibility.

### Security

- Reduced sensitive logging and protected generated exports.
- Removed the legacy credential-based login flow.

Versions through 1.3.2 belong to the upstream project history.

[Unreleased]: https://github.com/alsd4git/fb2cal/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/alsd4git/fb2cal/compare/v1.3.2...v2.0.0
