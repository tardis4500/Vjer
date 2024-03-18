#!/usr/bin/env python
"""This program provides deployment job actions."""

# Import standard module
import os
from pathlib import Path
from shutil import copyfile, copytree
from typing import cast

# Import third-party modules
from batcave.k8s import Cluster
from batcave.lang import yaml_to_dotmap
from batcave.sysutil import rmpath, syscmd
from dotmap import DotMap

# Import project modules
from utils import PKG_EXT, PROJECT_CFG_VAR, helm, CICDAction, CICDStep


class DeployStep(CICDStep):
    """This class provides deployment support."""

    def deploy_ansible(self) -> None:
        """Deploy method for Ansible playbooks."""
        self.run_ansible_playbook()

    def deploy_exec(self) -> None:
        """Deploy method for syscmd runner."""
        syscmd(self.step_info.command, *self.step_info.args, **({'show_cmd': True, 'show_stdout': True, 'use_shell': True} | self.step_info.executor_args))

    def deploy_filecopy(self) -> None:
        """Deploy method to copy files."""
        source_root = Path(self.project.artifacts_dir)
        target_root = Path(self.step_info.target)
        if self.step_info.clean and target_root.exists():
            self.log_message(f'Removing "{target_root}"')
            rmpath(target_root)
        target_root.mkdir(parents=True, exist_ok=True)
        for artifact in self.step_info.files:
            src = source_root / artifact['name']
            target = target_root / (artifact['target'] if ('target' in artifact) else src.name)
            if artifact.get('overwrite', True) or not target.exists():
                self.log_message(f'Copying "{src}" to "{target}"')
                if src.is_dir():
                    copytree(str(src), str(target), dirs_exist_ok=True)
                else:
                    copyfile(src, target)

    def deploy_helm(self) -> None:
        """Deploy method for Helm charts."""
        chart_name = self.step_info.chart_name if self.step_info.chart_name else self.project.product.lower()
        release_name = self.step_info.release_name.lower() if self.step_info.release_name else chart_name
        helm_args = self.helm_args
        is_remote = (self.step_info.remote is not False) and (self.step_info.remote or self.gitlab.CI_ENVIRONMENT_NAME.startswith('staging')
                                                              or self.gitlab.CI_ENVIRONMENT_NAME.startswith('production'))  # noqa:W503
        if is_remote:
            helm_chart = f'{self.helm_repo.name}/{chart_name}'
            if 'version' not in helm_args:
                helm_args['version'] = self.project.version
        else:
            helm_chart = self.helm_package
        if is_remote:
            helm('repo', 'update')
        helm('upgrade', release_name, helm_chart, install=True, atomic=True, wait=True, **helm_args)

    def deploy_k8s(self) -> None:
        """Deploy method for Kubernetes."""
        cluster = Cluster(self.step_info.kubeconfig, self.step_info.k8s_cluster)
        kubectl_args = []
        if self.step_info.namespace:
            cluster.create_namespace(self.step_info.namespace, exists_ok=True)
            kubectl_args = ['--namespace', self.step_info.namespace]
        for line in cluster.kubectl('apply', '--filename', self.project.artifacts_dir / 'kubernetes', *kubectl_args):
            self.log_message(line.strip())

    def deploy_package(self) -> None:
        """Publish a package to a bucket."""
        package_name = self.step_info.package_name if self.step_info.package_name else self.project.product
        self.publish_package(self.step_info.package_dir, f'{package_name}-{self.gitlab.CI_ENVIRONMENT_NAME}{PKG_EXT}', exists_ok=True)

    def deploy_qb(self) -> None:
        """Deploy to QuickBuild."""
        self.qb_deploy()

    def deploy_umbrella(self) -> None:
        """Deploy a set of Helm charts."""
        for component_dict in self.project.components:
            component = DotMap(component_dict)
            env_vars = DotMap({PROJECT_CFG_VAR: str((self.project.artifacts_dir / component.name).with_suffix('.yml'))})
            if (var_file := (self.project.artifacts_dir / f'{component.name}-vars').with_suffix('.yml')).exists():
                env_vars |= yaml_to_dotmap(var_file)
            for (var, value) in env_vars.items():
                os.environ[var] = value
            CICDAction('deploy', cast(CICDStep, DeployStep)).execute()


def main() -> None:
    """This is the main entry point."""
    CICDAction('deploy', cast(CICDStep, DeployStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore batcave cicd fileutil kubeconfig filecopy dnsname dotmap syscmd
