===============
Version History
===============

v1.12.0
-------

* Add move_bucket_ticket_links script
* Add collect_ticket_commits script

v1.11.1
-------

* Add dash parsing support to check_software_releases
* Add node and stack_ra to ignore list
* Add ts_cbp and ts_tunablelaser repos to rename dictionary

v1.11.0
-------

* Change Jira URL to cloud version
* Update Jira auth in all scripts that require it
* Update fields in scripts that create Jira tickets
* Add Jira user search ticket helper function

v1.10.3
-------

* Add hardware text for summit in release_annoucement

v1.10.2
-------

* Update repository mapping for check_software_releases

v1.10.1
-------

* Update repository mapping and ignore list for check_software_releases

v1.10.0
-------

* Add extra information to ticket generated from create_summit_upgrade_ticket

  * Task participants
  * Description
  * Labels

v1.9.0
------

* Add create_summit_upgrade_ticket script and associated module
* Documentation fixes
* Updates for release_announcement.py

  * Add Base test stand handling
  * Add hour prior announcement message

v1.8.0
------

* Add create_configuration_tickets script and associated module
* Documentation fixes

v1.7.1
------

* Updates for check_software_releases.py

  * Add mapping for ts_criopy package
  * Protect against blank lines in cycle.env

v1.7.0
------

* Fix module name for check_software_releases script
* Updates for check_software_releases.py

  * Updated ignore list
  * Updated repository mapping
  * Added recipe mapping and handling
  * Fixed order of tags from GraphQL call
  * Fixed version handling

* Added ts-pre-commit-config setup
* Updated README.md for development


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
