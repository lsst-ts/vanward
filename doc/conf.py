"""Sphinx configuration file for an LSST stack package.
This configuration only affects single-package Sphinx documentation builds.
"""

import lsst.ts.vanward  # noqa
from documenteer.conf.guide import *  # noqa

project = "vanward"
html_theme_options["logotext"] = project  # type: ignore  # noqa
html_title = project
html_short_title = project
doxylink = {}  # type: ignore # Avoid warning: Could not find tag file _doxygen/doxygen.tag
