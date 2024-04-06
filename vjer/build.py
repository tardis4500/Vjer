"""This module provides build actions."""

# Import standard modules
from os import getenv
from pathlib import Path
from shutil import copyfile
from tempfile import mkdtemp
from typing import cast, Optional

# Import third-party modules
from batcave.fileutil import pack
from batcave.lang import str_to_pythonval
from batcave.sysutil import rmpath
from docker.errors import BuildError as DockerBuildError

# Import project modules
from .utils import VJER_ENV, VjerAction, VjerStep, helm


class BuildStep(VjerStep):
    """This class provides build support.

        Build processing flow:
          pre:
              remove an old artifact directory
              create the artifact directory
              update the version files
          execute:
              run the inheriting build() method for the project type
          post:
              revert the version files
    """
    def pre(self) -> None:
        """This method is run at the start of the build."""
        super().pre()
        if self.step_info.is_first_step:
            self.log_message('Preparing artifact directory', True)
            if Path(self.project.artifacts_dir).exists():
                self.log_message(f'Removing stale artifact directory: {self.project.artifacts_dir}')
                rmpath(self.project.artifacts_dir)
            if not Path(self.project.artifacts_dir).exists():
                self.log_message(f'Creating clean artifact directory: {self.project.artifacts_dir}')
                Path(self.project.artifacts_dir).mkdir(parents=True)
        self.update_version_files()

    def post(self) -> None:
        """This method is run at the end of the build."""
        super().post()
        self.log_message('Build Completed Successfully', True)

    def always_post(self) -> None:
        """This method is always run at the end of the build."""
        super().always_post()
        self.update_version_files(reset=True)

    def create_archive(self, name: str, what: list, /, *, location: Optional[str] = None, arc_type: Optional[str] = None, use_tmpdir: bool = False) -> None:  # pylint: disable=too-many-arguments
        """Helper function to create an archive. When complete, the archive is copied to the project build artifact directory.

        Args:
            name: The archive file name.
            what: The files to include in the archive.
            location (optional, default=None): The location of the files to archive. If None, the current directory is used.
            arc_type (optional, default=None): The type of the archive. If None, is inferred from the file extension.
            use_tmpdir (optional, default=False): If True, create the archive in a temporary directory.

        Returns:
            Nothing.
        """
        package_dir = Path(mkdtemp()) if use_tmpdir else self.project.artifacts_dir
        package = package_dir / name
        try:
            self.log_message(f'Creating "{package}" archive from: {",".join(what)}', True)
            pack(package, what, item_location=location, archive_type=str(arc_type), ignore_empty=False)
            copyfile(package, self.project.artifacts_dir / name)
        finally:
            if use_tmpdir:
                rmpath(package_dir)

    def build_docker(self) -> None:
        """Run a Docker build."""
        push_image = str_to_pythonval(getenv('VJER_DOCKER_PUSH', str(not VJER_ENV == 'local')))
        self._docker_init(push_image)
        self.log_message(f'Building docker image: {self.image_tag}', True)
        build_args = {'VERSION': self.project.version,
                      'BUILD_VERSION': self.build.build_version} | self.step_info.build_args
        platform_arg = {'platform': platform} if (platform := getenv('DOCKER_DEFAULT_PLATFORM', '')) else {}
        try:
            log = self.docker_client.client.images.build(rm=True, pull=True, tag=self.image_tag,
                                                         dockerfile=(self.dockerfile),
                                                         buildargs=build_args.toDict(),
                                                         path=str(self.project.project_root),
                                                         **platform_arg)[1]
            error = None
        except DockerBuildError as err:
            error = err
            log = err.build_log
        for line in log:
            if ('stream' in line) and (line['stream'] != '\n'):
                self.log_message(line['stream'].strip())
        if error:
            raise error
        if push_image:
            self.log_message('Pushing image to registry', True)
            self.registry_client.get_image(self.image_tag).push()

    def build_flit(self) -> None:
        """Run a Python flit build."""
        self.flit_build()

    def build_helm(self) -> None:
        """Build method for Helm charts."""
        helm('dependency', 'build', self.helm_chart_root)
        helm('package', self.helm_chart_root)
        self.copy_artifact(self.helm_package.name)


def build() -> None:
    """This is the main entry point."""
    VjerAction('build', cast(VjerStep, BuildStep)).execute()

# cSpell:ignore batcave fileutil pythonval buildargs vjer
