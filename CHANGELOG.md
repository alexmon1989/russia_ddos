# Change Log
All notable changes to this project will be documented in this file.

The format based on [Keep a Changelog](https://keepachangelog.com)
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased](https://github.com/alexmon1989/russia_ddos/compare/2.1.0...HEAD)

### Added
- Command line Option `--version` to get the current version of script
- Added support for HTTP and SOCKS4 proxy.
- Added the possibility to read proxies from HTTP/HTTPS location. It helps organize multiple peers.

### Changed
- UDP/TCP/HTTP attack methods internals
- HTTP Status code check method now support periodical check


## [v2.1.0](https://github.com/alexmon1989/russia_ddos/compare/2.0.4...2.1.0)


### Added
- Added support for SOCKS5 proxies. (HTTP/TCP only)
- Added possibility to dismiss health check. It is helpful during development.
- Added the possibility to attack random extra_data for HTTP attack (turned off by default).
- Added build tools to create `dripper` executable for Windows/Linux/macOS

### Fixed
- Fixed proxy list params read

### Changed
- Reworked Error log for Statistic


## [v2.0.4](https://github.com/alexmon1989/russia_ddos/compare/2.0.3...2.0.4)

### Changed
- Moved options parser to separate module
- Simplified health check logic
- Improved script start time


## [v2.0.3](https://github.com/alexmon1989/russia_ddos/compare/2.0.3...2.0.3)

### Fixed
- Fixed vertical scrolling issue
- Fixed live refresh for Statistic


## [v2.0.2](https://github.com/alexmon1989/russia_ddos/compare/2.0.1...2.0.2)

### Fixed
- Fixed bug with missed property for Packets statistic [#37](https://github.com/alexmon1989/russia_ddos/issues/37)


## [v2.0.1](https://github.com/alexmon1989/russia_ddos/compare/2.0.0...2.0.1)

### Fixed
- Fixed bug with missed property for Packets statistic [#37](https://github.com/alexmon1989/russia_ddos/issues/37)


## [v2.0.0](https://github.com/alexmon1989/russia_ddos/compare/1.3.9...2.0.0)

### Changed
- Simplified logic
- Reworked statistic
- Other code improvements

### Fixed
- Fixed several bugs


## [v1.3.9](https://github.com/alexmon1989/russia_ddos/compare/1.3.8...1.3.9)

### Added
- Added country detection and displaying in Statistic

### Changed
- Optimized UDP attack
- Minor improvements


## [v1.3.8](https://github.com/alexmon1989/russia_ddos/compare/1.3.7...1.3.8)

### Added
- Added CloudFlare detection
- Added support for cross-platform colored CLI output

### Changed
- Improved performance
- Improved UI

### Fixed
- Fixed several bugs


## [v1.3.7](https://github.com/alexmon1989/russia_ddos/compare/1.3.6...1.3.7)

### Fixed
- Fixed several bugs


## [v1.3.6](https://github.com/alexmon1989/russia_ddos/compare/1.3.5...1.3.6)

### Added
- Added version displaying in header
- Added Python 3.8 support

### Fixed
- Fixed several bugs


## [v1.3.5](https://github.com/alexmon1989/russia_ddos/compare/1.3.4...1.3.5)

### Added
- Added TCP flood

### Fixed
- Fixed check connection


## [v1.3.4](https://github.com/alexmon1989/russia_ddos/compare/1.3.1...1.3.4)

### Added
- Added ARM support for Docker builds


## [v1.3.1](https://github.com/alexmon1989/russia_ddos/compare/1.3.0...1.3.1)

### Added
- Added validation


## [v1.3.0](https://github.com/alexmon1989/russia_ddos/compare/1.1.0...1.3.0)

### Changed
- Improved logging

### Fixed
- Fixed IndexOutOfBound Exception


## [v1.1.0](https://github.com/alexmon1989/russia_ddos/compare/1.1.0...1.1.0)

### Changed
- Changed UI
- Improved speed

