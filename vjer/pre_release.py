"""This module provides pre-release actions."""

# Import standard modules
from typing import cast

# Import project modules
from .release import ReleaseStep
from .utils import VjerAction, VjerStep, helm


class PreReleaseStep(ReleaseStep):
    """Provide pre_release support.

    Attributes:
        is_pre_release: Specifies to the ReleaseStep parent class that this is a pre-release action.
    """
    is_pre_release = True

    def __init__(self):
        """Sets the project version to a pre-release value."""
        super().__init__()
        self.project.version = f'{self.project.version}-{self.pre_release_num}'

    def release_helm(self) -> None:
        """Pre-release a Helm chart."""
        if self.helm_repo.type == 'oci':
            self.update_version_files()
            try:
                helm('package', self.helm_chart_root)
                self.copy_artifact(self.helm_package.name)
            finally:
                self.update_version_files(reset=True)
        else:
            list(self.project.artifacts_dir.glob('*.tgz'))[0].rename(self.helm_package)
        super().release_helm()


def pre_release() -> None:
    """This is the main entry point."""
    VjerAction('release', cast(VjerStep, PreReleaseStep)).execute()

# cSpell:ignore batcave vjer
