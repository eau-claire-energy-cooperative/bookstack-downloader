# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## Version 2.0

### Added

- added `--modified-only` flag. This will only download books changed since the last run of the script, utilizing a `last_run.txt` bookmark file.

### Fixed

- fixed unintended else conditional when running in `--test` mode. Removes some unnecessary print statements during test run. 

## Version 1.1

### Added

- added `--test` flag to run in test mode. No files will be downloaded in test mode but all output is shown

## Version 1.0

### Added

- release of first version, can connect and download books/shelves
