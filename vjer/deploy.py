"""This module provides deployment actions."""

# Import standard module
from typing import cast

# Import project modules
from .utils import helm, VjerAction, VjerStep


class DeployStep(VjerStep):
    """This class provides deployment support."""

    def deploy_helm(self) -> None:
        """Deploy method for Helm charts."""
        chart_name = self.step_info.chart_name if self.step_info.chart_name else self.project.name.lower()
        release_name = self.step_info.release_name.lower() if self.step_info.release_name else chart_name
        helm_args = self.helm_args
        is_remote = self.step_info.remote is not False
        if is_remote:
            helm_chart = f'{self.helm_repo.name}/{chart_name}'
            if 'version' not in helm_args:
                helm_args['version'] = self.project.version
        else:
            helm_chart = self.helm_package
        if is_remote:
            helm('repo', 'update')
        helm('upgrade', release_name, helm_chart, install=True, atomic=True, wait=True, **helm_args)


def deploy() -> None:
    """This is the main entry point."""
    VjerAction('deploy', cast(VjerStep, DeployStep)).execute()

# cSpell:ignore vjer
