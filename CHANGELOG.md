# Change Log
All notable changes to this project will be documented in this file.

The format based on [Keep a Changelog](https://keepachangelog.com)
and this project adheres to [Semantic Versioning](https://semver.org).

## [Unreleased](https://github.com/alexmon1989/russia_ddos/compare/2.6.3...HEAD)


## [v2.6.3](https://github.com/alexmon1989/russia_ddos/compare/2.6.2...2.6.3)

## Changed
- Moved initial checks to attacks to speedup script start

### Fixed
- Fixed error with Request lib import


## [v2.6.2](https://github.com/alexmon1989/russia_ddos/compare/2.6.1...2.6.2)

### Fixed
- Fixed error with encoding for external resources (targets list)


## [v2.6.1](https://github.com/alexmon1989/russia_ddos/compare/2.6.0...2.6.1)

### Fixed
- Fixed timeouts
- Fixed script start logic

## [v2.6.0](https://github.com/alexmon1989/russia_ddos/compare/2.5.0...2.6.0)

### Added
- Attack duration param (in seconds). After this duration script will stop its execution.
- User guide and setup guide
- Threads count autoscaling. `-t` argument (same as `--threads-count`) now supports **auto**. The auto-scaling method is the default.
- Check minimal required python version
- Attack duration controller. `-d` argument (same as `--duration`) set the attack duration in seconds. After this duration script will stop its execution.
- Targets list support. `--targets-list` argument allows you to use list with targets. List with targets can be path to file or hyperlink.

### Changed
- Random bytes optimization (performance improvement)
- Changed CLI arguments for package size management
- Improved speed for new version check
- Improved text messages for better user experience

### Fixed
- Fixed command parameter generator to help users with incorrect command line parameters or errors with parameters
- Test UDP connection for UDP scheme if TCP did not work


## [v2.5.0](https://github.com/alexmon1989/russia_ddos/compare/2.4.0...2.5.0)

### Added
- Check DRipper updates from GitHub tags and show notification to user about it.
- Added check for anti-DDoS page protection for check-host.net service.
- Script command parameter generator to help users with incorrect command line parameters or errors with parameters

### Changed
- Changed multiple target argument pass. Targets should be passed separately with `-s` flag.
- Moved target specific validation from statistic and context to Target class
- Targets manager can allocate attacks after target is removed and encapsulates logic related to the targets collection management.


## [v2.4.0](https://github.com/alexmon1989/russia_ddos/compare/2.3.1...2.4.0)

### Added
- Added support for multiple targets. Multiple target should be passed as sting with ',' as delimiter
- Threads are distributed uniformly between targets.
- Irresponsive targets and their threads die in runtime.
- Added support for the log-level argument.

### Changed
- Target-related stats are represented on pages. Pages are rotated automatically in 5 seconds intervals.
- Refactored stats representation. Isolated target-related details builder.
- Isolated time interval manager.
- Improved error messages and description about error when validates input arguments.

### Fixed
- Fixed CloudFlare detection logic.


## [v2.3.1](https://github.com/alexmon1989/russia_ddos/compare/2.3.0...2.3.1)

### Fixed
- Fixed setup script and Docker builds


## [v2.3.0](https://github.com/alexmon1989/russia_ddos/compare/2.2.0...2.3.0)

### Added
- `dry run` mode for fast testing purposes
- CloudFlare bypass mode for HTTP flood method
- Events log that helps to understand attack process details in depth
- `--log-size` parameter to configure Events log history frame length

### Fixed
- Fixed error with keyboard interrupting and threads shutdown process
- Reduced IP address re-checks to avoid redundant API calls
- Attack checks methods, improved speed
- Rendering table with statistic does not re-render table caption with logo

### Changed
- Isolated target. The target contains a full server description, statistics, and health check. It is an intermediate step towards multiple targets.
- Formalized attack_method, added names and labels for attacks.
- Isolated assets.
- Split context on components.
- Changed health check to be target-dependant.
- Reduced awareness about the entire context structure.
- Unified tests format. Classes should represent "Describe" blocks, and test methods should start with "it."
- Changed Exception handling and logging process.
- Replaced Error class with Events


## [v2.2.0](https://github.com/alexmon1989/russia_ddos/compare/2.1.0...2.2.0)

### Added
- Command line Option `--version` to get the current version of script
- Added support for HTTP and SOCKS4 proxy.
- Added the possibility to read proxies from HTTP/HTTPS location. It helps to organize multiple peers.

### Changed
- UDP/TCP/HTTP attack methods internals
- HTTP Status code check method now support periodical check
- Improved performance for HTTP flood


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

