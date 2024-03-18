#!/usr/bin/env python
"""This programs provides release job actions."""

# Import standard modules
from pathlib import Path
from sys import exit as sys_exit
from typing import cast

# Import third-party modules
from dotmap import DotMap
from jira import JIRA
from requests import codes, delete, get, post
from twine.commands.upload import main as pypi_upload

# Import project modules
from utils import GitLab, gcloud, helm, CICDAction, CICDStep


class ReleaseStep(CICDStep):
    """Provide release support.

    Attributes:
        is_pre_release: Specifies that this is not a pre-release action.
    """
    is_pre_release = False

    def release_ansible(self) -> None:
        """Publish an Ansible playbook."""
        self.publish_package(self.ansible_dir, self.pkg_archive)

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
                case 'jfrog':
                    (image_name, image_version) = self.image_tag.split(':')
                    image_name = image_name.split('/')[-1]
                    tag_name = tag.split(':')[-1]
                    target = f'{registry.name}/{image_name}/{tag_name}'
                    call_args = DotMap(headers={'Authorization': f'Bearer {registry.auth[1]}'}, timeout=60, verify=False)
                    response = get(f'{registry.push_url}/artifactory/api/storage/{target}', **call_args)
                    if response.status_code == codes.ok:  # pylint: disable=no-member
                        (response := delete(f'{registry.push_url}/artifactory/{target}', **call_args)).raise_for_status()
                    elif response.status_code != codes.not_found:  # pylint: disable=no-member
                        response.raise_for_status()
                    (response := post(f'{registry.push_url}/artifactory/api/copy/{registry.name}/{image_name}/{image_version}?to=/{target}', **call_args)).raise_for_status()
                case  _:
                    image.tag(tag)
                    image.push()

    def release_file(self, *, exists_ok: bool = False) -> None:
        """Release a list of files.

        Args:
            exists_ok (optional, default=False): If False, raise an error if the file already exists.

        Returns:
            Nothing.

        Raises:
            StepError.DUPLICATE_PUBLISH: If the file already exists.
        """
        for release_file_spec in self.step_info.files:
            release_file_path = Path(release_file_spec)
            for release_file_name in self.project.artifacts_dir.glob(f'{release_file_path.stem}*{release_file_path.suffix}'):
                self.publish_package(release_file_name, exists_ok=exists_ok)

    def release_gitlab(self) -> None:
        """Create a GitLab release."""
        if self.is_pre_release:
            self.log_message('Skipping on pre-release')
            return
        assets = {} if not self.step_info.publish_artifacts else \
            {'assets': {'links': [{'name': 'Artifacts', 'url': f'{self.gitlab.CI_ARTIFACTS_URL}/-/jobs/{self.gitlab.CI_JOB_ID}/artifacts/download'}]}}
        response = post(self.gitlab.CI_RELEASES_API,
                        headers={'Content-Type': 'application/json', 'Private-Token': self.gitlab.GITLAB_USER_TOKEN},
                        timeout=60,
                        verify=False,
                        json={'name': f'Release {self.project.version}',
                              'tag_name': f'{self.release.release_tag}',
                              'description': f'Release {self.project.version}',
                              **assets})
        response.raise_for_status()

    def release_helm(self) -> None:
        """Perform a release of a Helm chart."""
        match self.helm_repo.type:
            case 'chartmuseum':
                plugin = 'cm-push'
            case 'jfrog':
                plugin = 'push-artifactory'
            case _:
                plugin = 'push'
        helm(plugin, self.helm_package, self.helm_repo.push_url if self.helm_repo.push_url else self.helm_repo.name, version=self.project.version, **self.helm_repo.push_args)

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
        use_branch = self.step_info.increment_branch if self.step_info.increment_branch else self.gitlab.CI_COMMIT_REF_NAME
        self.project.version = new_version
        self.log_message(f'Incrementing release to {new_version} on branch {use_branch}')
        self.commit_files('Automated pipeline version update check-in [skip ci]', use_branch, self.config.filename, file_updater=self.config.write)

    def release_jira(self) -> None:
        """Create a JIRA ticket for a staging deploy request."""
        if (not self.is_pre_release) and self.step_info.pre_release_only:
            self.log_message('Skipping on release')
            return
        jira = JIRA(self.gitlab.JIRA_URL, basic_auth=(self.gitlab.JIRA_USER, self.gitlab.JIRA_TOKEN))
        ticket_description = f'Build to deploy: {self.project.version}\nRequested by: {self.gitlab.GITLAB_USER_NAME}'
        if self.step_info.extra_info:
            ticket_description += f'\n{self.step_info.extra_info}'
        issue = jira.create_issue(project='SRE', issuetype={'name': 'Story'},
                                  summary=f'{self.project.product} Staging Deploy Request',
                                  description=ticket_description)
        self.log_message(f'Created JIRA issue for staging deploy request: {issue}')

    def release_python_module(self) -> None:
        """Publish to the specified PyPi server."""
        pypi_upload([f'--repository-url={self.step_info.repo_url if self.step_info.repo_url else self.gitlab.CI_PYPI_URL}',
                     f'--user={self.step_info.user if self.step_info.user else "gitlab-ci-token"}',
                     f'--password={self.step_info.password if self.step_info.password else self.gitlab.CI_JOB_TOKEN}',
                     f'{self.project.artifacts_dir}/*'])

    def release_tag_source(self) -> None:
        """Tag the source in GitLab with a release tag."""
        if self.is_pre_release:
            self.log_message('Skipping on pre-release')
            return
        self.tag_source(self.release.release_tag, f'Release {self.release.release_tag}')

    def release_umbrella(self, action: str = 'release') -> None:
        """Perform an umbrella release."""
        for component_dict in self.project.components:
            component = DotMap(component_dict)
            self.log_message(f'Processing: {component.name}')
            with GitLab(project_id=component.id) as gitlab_project:
                if (result := gitlab_project.run_job(action))['status'] != 'success':
                    self.log_message(f'Error in pre-release: {result["failure_reason"]}')
                    sys_exit(1)

    def release_update_versions(self, action: str = 'release') -> None:
        """Update the versions in a deployment project file."""
        for component in self.step_info.components:
            self.log_message(f'Processing: {component.name}...')
            with GitLab(component.id, branch=component.branch) as gitlab_project:
                component_version = gitlab_project.latest_build_num
            if action == 'release':
                component_version = component_version.split('-')[0]
            self.log_message(f'  found: {component_version}...')
            # product_cfg_updated['components'].append(component)
        # dotmap_to_yaml(product_cfg_updated, product_cfg_file.with_suffix('.new'))


def main() -> None:
    """This is the main entry point."""
    CICDAction('release', cast(CICDStep, ReleaseStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore batcave cicd checkin fileutil syscmd dotmap chartmuseum
