===============
Version History
===============

v1.7.0
------

* Fix module name for check_software_releases script

v1.6.0
------

* Switch to pyproject.toml packaging
* Executable scripts no longer have the .py extension
* Modules that drive the scripts have the same name but with the .py extension
* Update find_merges_without_release_tickets to add parent ticket for branch checks
* Update check_software_releases for package changes

v1.5.0
------

* Update release_announcement.py script for TTS

  * Add system readiness time
  * Unify and simplify datetime handling from options

* Updates for check_software_releases.py

  * Fix directory for recipe packages
  * Add mapping for ts_mtaircompressor package
  * Fix version handling for config packages

* Added check_conda_package_versions.py to installation

v1.4.1
------

* Remove NCSA test stand from release_annoucement.py script

v1.4.0
------

* Renamed ts_ess_csc conda package from ts-ess to ts-ess-csc
* Added several labjack items, openjdk and maven to ignore list

v1.3.0
------

* Added a script to verify that conda packages exist for all cycle packages and versions

v1.2.1
------

* Fixed issues with check_software_releases.py

  * Add obs_lsst to ignore list
  * Map ts_integrationtests

v1.2.0
------

* Skip *is triggered* linked issues in release_tickets.py

v1.1.0
------

* Fixed issues with check_software_releases.py

  * Fixed repository mapping
  * Fixed handling of repository only packages

v1.0.0
------

* Initial release of the scripts
