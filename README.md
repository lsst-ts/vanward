# Vanward

This package contains scripts that are used prior to certain steps within
the deployment process.

[Documentation](https://vanward.lsst.io)

This code uses a pre-commit hook to maintain compliance with TSSW software standards.
To enable this, in a virtual environment, do the following after cloning the repository:
 
  * pip install -e .[dev]
  * conda install -c lsstts ts-pre-commit-config
  * generate_pre_commit_conf
  * pre-commit install
