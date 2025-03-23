# Changelog

All notable changes to the DGT RPC Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Support for asynchronous operations
- Improved error handling with detailed error messages

## [1.0.0] - 2023-12-15
### Added
- Initial stable release
- Complete documentation
- Comprehensive test suite

## [0.2.0] - 2023-11-10
### Added
- DgtPOSClient for specialized POS operations
- Configuration file support
- Environment variable support
- Connection pooling for improved performance

### Changed
- Improved error handling
- Enhanced authentication caching

### Fixed
- Issue with XML-RPC timeout handling
- Authentication failure with special characters in passwords

## [0.1.0] - 2023-10-01
### Added
- Initial release
- Basic DgtClient implementation
- Support for common Odoo operations (search, read, create, write, unlink)
- Authentication via username/password and API key
- Basic error handling

[Unreleased]: https://github.com/dgtera/dgt-rpc/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/dgtera/dgt-rpc/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/dgtera/dgt-rpc/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dgtera/dgt-rpc/releases/tag/v0.1.0 