.. py:currentmodule:: lsst.ts.vanward

.. |Michael Reuter| replace::  *mareuter@lsst.org*

.. _lsst.ts.vanward:

###############
lsst.ts.vanward
###############

.. _lsst.ts.vanward.overview:

Overview
========

This packages contains scripts that assist in situations prior to some of the steps along the road to a deployment.
Each of the scripts and the situations for their use will be described in the section below.

.. _lsst.ts.vanward.user_guide:

User Guide
==========

.. note::

 Five of the scripts below require authentication information provided by a file.
 Please make sure those authentication files are read-only user (600).

Preparing for a Cycle Upgrade
-----------------------------

When the schedule for the cycle upgrade has been set, a ticket must be created on the `Summit Jira <https://jira.lsstcorp.org/projects/SUMMIT>`_ to inform the summit folks an upgrade is coming.
The ``create_summit_upgrade_ticket`` script can assist in the creation of that ticket.
An example usage of the script is shown here:

.. prompt:: bash

  create_summit_upgrade_ticket 31 2023-06-20

This script leverages the ``.jira_auth`` in your home directory.
There is an optional argument to change the assignee of the ticket.
The assignee should make sure to attend both the Summit Activities Planning meeting and the Weekly Summit Coordination meeting.
Use the ``--help`` flag on the script for more information.

Preparing for a XML Release
---------------------------

When wrapping up the work for a XML release, which usually kicks off a new cycle build, you need to check if all of the work that is merged into the `ts_xml <https://github.com/lsst-ts/ts_xml.git>`_ repository has a corresponding Jira ticket as specified by the `Reporting Work for XML Release <https://tssw-developer.lsst.io/procedures/reporting-xml-release-work.html>`_.
The ``find_merges_without_release_tickets`` script handles this type of check and an example usage for the script is shown here:

.. prompt:: bash

  find_merges_without_release_tickets ~/git 9.0 v9.0.0

The first argument is the path to the local clone of the ``ts_xml`` repository and this will vary depending on where your clone lives.
The second argument is the numeric portion of the Releases label used in the CAP Jira project for the given XML release.
The third argument is the tag on the ``ts_xml`` repository that represents the previous XML release.
The output of the script will highlight tickets that have been merged on the repository that do not have tickets in the Jira release.

The Jira tickets associated with the release also need to be checked to ensure that they are closed or marked appropriately before considering the XML work for the release wrapped up and ready for building the base artifacts.
The ``release_tickets`` script handles this type of check and an example usage is shown here:

.. prompt:: bash

  release_tickets 9.0

The argument is the numeric portion of the Releases label used in the CAP Jira project for the given XML release.

Both scripts require authentication to the project Jira site.
Those are provided by a file (``.jira_auth``) in your home directory containing a line each for your Jira username and password.
An alternately named and located file can be used.
Use the ``--help`` flag on those scripts for more information.

Preparing for a Cycle Build
---------------------------

When readying for a cycle build, which generates the container images, the software versions contained within the `ts_cycle_build <https://github.com/lsst-ts/ts_cycle_build.git>`_ repository need to be checked against the latest tags in the associated repositories.
The ``check_software_releases`` script helps with this check.
It requires that the ``ts_cycle_build`` and the `ts_recipes <https://github.com/lsst-ts/ts_recipes.git>`_ are cloned to the same directory on your machine.
``ts_cycle_build`` should be made up-to-date on the master branch in order to ensure that all previous cycle revisions have been accounted for.
The same goes for the ``ts_recipes`` clone.
The script is run as follows:

.. prompt:: bash

  check_software_releases <path to repo clones>

The script reads the ``cycle/cycle.env`` file from the ``ts_cycle_build`` repository, queries organization GitHub repositories for the latest tag and compares the software versions to see if there are any differences.
If there are any differences, they are reported and look something like:

 .. code:: bash

   ts_ddsconfig: SoftwareVersions(current='0.6.2', latest='0.7.0')
   ts_sal: SoftwareVersions(current='5.1.1', latest='5.2.0')
   ts_idl: SoftwareVersions(current='3.1.3', latest='3.2.0')
   ts_salobj: SoftwareVersions(current='6.4.1', latest='6.5.2')
   ...

In order to make less calls against the GitHub API, all organization repositories are queried.
This makes the script run for on the order of 15 to 20 seconds before completing.
The script also requires an access token for API authentication.
The token string is provided in a file (``.gh_token``) in your home directory containing one line for the token string.
The authentication token is maintained by the Telescope and Site build and deployment team, so consult that group if the token is necessary for you to use.
An alternately named and located file can be used.
Use the ``--help`` flag on those scripts for more information.

Preparing Configuration
-----------------------

When getting ready to prepare the configuration for the first site in the deployment process, the configuration tickets for all the sites can be generated at the same time.
Those tickets can then be linked to the appropriate cycle build Confluence page.
The ``create_configuration_tickets`` script can help with this task.
This script leverages the ``.jira_auth`` in your home directory.
The script requires the cycle build number.
See the ``--help`` flag on the script for more detailed information about the options.
An example usage of the script is shown below:

.. prompt:: bash

  create_configuration_tickets 31

The output from the script will print the issue keys for each site for inclusion into the cycle build Confluence page.


Preparing for Deployment to a Site
----------------------------------

When preparing for deploying a cycle build to a site (summit or a test stand), the best practice is to place an announcement on the appropriate Slack channel the day before the deployment.
The ``release_announcement`` script can help with this task.
It has flags to support multiple sites, but only one of those flags can be specified for a given run of the script.
The date and time of the deployment as well as the cycle build number needs to be provided to the script.
The time of the deployment is specified in the local time of the site as the script does no time zone conversion.
If integration testing is taking place after the deployment at one of the test stands, the ending time of the testing needs to be specified to the script.
See the ``--help`` flag on the script for more detailed information about the options.
An example usage of the script is shown below:

.. prompt:: bash

  release_announcement -s 2021-06-29 17:00 21

The above incantation is for a summit deployment.

.. note::

  The script only outputs the string for the announcement.
  It is up to the user to post that output into the appropriate Slack channel before the deployment.

The script also provides text for a reminder announcement one hour prior to the deployment time.
That text should be scheduled via the `Timy Slack app interface <https://slack.timy.website/>`_ in the time zone appropriate for the site.

.. _lsst.ts.vanward.developer_guide:

Developer Guide
===============

Package Setup
-------------

Since this package contains scripts that leverage services that would require extensive mocking in order to provide unit tests, there are none provided at this time.
Therefore the usual build and test cycle is different for this package.
If you wish to fix, update or add new scripts to this package, the recommended method for development is to get the T&S development Docker container.
Instructions for this can be found `here <https://confluence.lsstcorp.org/display/LTS/CSC+Development>`_.
Follow the section on ``Developing on your own local folder on Docker``.
Since the code is not shipped with the development container, a clone of the code is necessary.

.. prompt:: bash

  git clone git@github.com:lsst-ts/vanward.git

Change or create the appropriate branch in the clone.

To setup the package, do the following.

.. code-block:: bash

    docker run -it --name {name for container} -v {repository_location}:/home/saluser/develop lsstts/develop-env:{tag}
    cd ~/develop/vanward
    pip install .

Building the Documentation
--------------------------

With the above setup completed, building the package documentation is done by:

.. prompt:: bash

  cd ~/develop/vanward
  package-docs build

Development Workflow
--------------------

Since this repository is dedicated to deployment, it follows a different development workflow than normal Telescope and Site packages.
The main difference is that there is no ``develop`` branch in the workflow.
Ticket branches are created from the main branch (currently called ``main``) and then pull requested and merged back into the main branch for tagging and release.
The repository is hooked to Telescope and Site Jenkins jobs for `documentation <https://tssw-ci.lsst.org/view/LSST_TandS/job/LSST_Telescope-and-Site/job/vanward/>`_ and the `conda package <https://tssw-ci.lsst.org/job/vanward/>`_, so pay attention to how those jobs are working.
Once a tag is created, a tagged conda build should be run to provide folks with the new version.

.. _lsst.ts.vanward.api:

API
===

The content in this section is autogenerated from docstrings.

.. automodapi:: lsst.ts.vanward
    :no-main-docstr:
    :no-inheritance-diagram:


.. _lsst.ts.vanward.version_history:

Version History
===============

The version history of vanward is found at the following link.

.. toctree::
    version-history
    :maxdepth: 1
