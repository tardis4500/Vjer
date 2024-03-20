"""This module provides release actions."""

# Import standard modules
from typing import cast

# Import third-party modules
from batcave.cloudmgr import gcloud

# Import project modules
from .utils import helm, VjerAction, VjerStep


class ReleaseStep(VjerStep):
    """Provide release support.

    Attributes:
        is_pre_release: Specifies that this is not a pre-release action.
    """
    is_pre_release = False

    def release_docker(self) -> None:
        """Perform a release of a Docker image by tagging."""
        self._docker_init()
        if (registry := self.container_registry).type not in ('gcp', 'jfrog'):
            (image := self.registry_client.get_image(self.image_tag)).pull()
        default_tags = [self.version_tag.lower()]
        if not self.is_pre_release:
            default_tags.append(f'{self.image_name}:latest'.lower())
        for tag in self.step_info.tags if self.step_info.tags else default_tags:
            self.log_message(f'Tagging image: {tag}')
            match registry.type:
                case 'gcp':
                    gcloud('container', 'images', 'add-tag', self.image_tag, tag, syscmd_args={'ignore_stderr': True})
                case  _:
                    image.tag(tag)
                    image.push()

    def release_helm(self) -> None:
        """Perform a release of a Helm chart."""
        helm('push', self.helm_package, self.helm_repo.name, **self.helm_repo.push_args)

    def release_increment_release(self) -> None:
        """Increment the project release version."""
        if self.is_pre_release:
            self.log_message('Skipping on pre-release')
            return
        if hasattr(self.project, 'version_service'):
            self.log_message('Incrementing version service not supported...skipping')
            return
        version_tuple = self.project.version.split('.')
        version_tuple[len(version_tuple) - 1] = str(int(version_tuple[-1]) + 1)
        new_version = '.'.join(version_tuple)
        use_branch = self.step_info.increment_branch if self.step_info.increment_branch else self.git_client.CI_COMMIT_REF_NAME
        self.project.version = new_version
        self.log_message(f'Incrementing release to {new_version} on branch {use_branch}')
        self.commit_files('Automated pipeline version update check-in [skip ci]', use_branch, self.config.filename, file_updater=self.config.write)

    def release_tag_source(self) -> None:
        """Tag the source in Git with a release tag."""
        if self.is_pre_release:
            self.log_message('Skipping on pre-release')
            return
        self.tag_source(self.release.release_tag, f'Release {self.release.release_tag}')


def release() -> None:
    """This is the main entry point."""
    VjerAction('release', cast(VjerStep, ReleaseStep)).execute()

# cSpell:ignore syscmd batcave cloudmgr vjer
