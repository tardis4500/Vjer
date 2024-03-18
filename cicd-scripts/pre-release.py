#!/usr/bin/env python
"""This programs provides pre-release job actions."""
# pylint: disable=invalid-name

# Import standard modules
from pathlib import Path
from typing import cast

# Import third-party modules
from batcave.sysutil import CMDError

# Import project modules
from release import ReleaseStep
from utils import CICDAction, CICDStep


class PreReleaseStep(ReleaseStep):
    """Provide pre-release support.

    Attributes:
        is_pre_release: Specifies to the ReleaseStep parent class that this is a pre-release action.
    """
    is_pre_release = True

    def __init__(self):
        """Sets the project version to a pre-release value."""
        super().__init__()
        self.project.version = f'{self.project.version}-{self.pre_release_num}'

    def release_file(self, *, exists_ok: bool = True) -> None:
        """Pre-release a list of files.

        Args:
            exists_ok (optional, default=True): If False, raise an error if the file already exists.

        Returns:
            Nothing.

        Raises:
            StepError.DUPLICATE_PUBLISH: If the file already exists.
        """
        artifact_files = {}
        for release_file_spec in self.step_info.files:
            release_file_path = Path(release_file_spec)
            for release_file_name in self.project.artifacts_dir.glob(f'{release_file_path.stem}*{release_file_path.suffix}'):
                release_file_name.rename(pre_release_file_name := self.project.artifacts_dir / f'{release_file_name.stem}-{self.pre_release_num}{release_file_name.suffix}')
                artifact_files[release_file_name] = pre_release_file_name
        try:
            super().release_file(exists_ok=exists_ok)
        finally:
            for (original, pre_release) in artifact_files.items():
                pre_release.rename(original)

    def release_helm(self) -> None:
        """Pre-release a Helm chart."""
        list(self.project.artifacts_dir.glob('*.tgz'))[0].rename(self.helm_package)
        try:
            super().release_helm()
        except CMDError as err:
            if 'Error: 409' not in ''.join(err.vars['errlines']):
                raise
            self.log_message('Skipping pre-release of Helm chart: chart already exists at this version')

    def release_umbrella(self, action: str = 'pre-release') -> None:
        """Pre-release a component collection."""
        super().release_umbrella(action=action)

    def release_update_versions(self, action: str = 'pre-release') -> None:
        """Update latest pre-release versions."""
        super().release_update_versions(action=action)


def main() -> None:
    """This is the main entry point."""
    CICDAction('release', cast(CICDStep, PreReleaseStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore cicd errlines batcave
