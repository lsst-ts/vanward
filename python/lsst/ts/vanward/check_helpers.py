"""Check script helpers.

Attributes
----------
IGNORE_LIST : `list`
    Packages in the cycle build file that are not checked.
ORG_LIST : `list`
    The GitHub organizations to query for the version information.
RECIPES_HANDLING : `list`
    Packages that are handled using the recipes mechanism.
REPOSITORY_MAP : `dict`
    Mapping of packages to GitHub repository names.
"""
from dataclasses import dataclass

__all__ = [
    "IGNORE_LIST",
    "ORG_LIST",
    "RECIPES_HANDLING",
    "REPOSITORY_MAP",
    "SoftwareVersions",
]


@dataclass
class SoftwareVersions:
    """Holder for the current and latest software versions."""

    current: str
    latest: str = None

    def is_latest(self) -> bool:
        """
        Returns
        -------
        bool
            True if the current and latest versions match. False otherwise.
        """
        if self.latest is None:
            return False
        return self.current == self.latest


ORG_LIST = ["lsst-ts", "lsst", "lsst-dm"]

IGNORE_LIST = [
    "CYCLE",
    "rev",
    "deploy_env",
    "hub",
    "ts_idl_git",
    "B_UID",
    "B_GID",
    "lsstsqre",
    "stack",
    "dds_community_version",
    "dds_community_build",
    "ts_dds_community",
    "ts_dds_community_conda_build",
    "dds_private_version",
    "dds_private_build",
    "ts_dds_private",
    "ts_dds_private_conda_build",
    "lsst_sims",
    "cwfs",
    "Spectractor",
    "obs_base",
    "pipe_tasks",
    "rapid_analysis",
    "atmospec",
    "ts_observing_utilities",
    "black_v",
    "gphoto2",
    "java_v",
    "obs_lsst",
    "openjdk",
    "maven",
    "labjack_file_version",
    "labjack_python_file_version",
    "labjack_arch",
    "labjack_c_version",
    "labjack_python_version",
]

RECIPES_HANDLING = ["ts_conda_build", "ts_develop"]

REPOSITORY_MAP = {
    "love_commander": "LOVE-commander",
    "love_producer": "LOVE-producer",
    "love_frontend": "LOVE-frontend",
    "love_manager": "LOVE-manager",
    "ts_mtaos": "ts_MTAOS",
    "ts_integrationtests": "ts_IntegrationTests",
    "ts_mtaircompressor": "ts_MTAirCompressor",
}
