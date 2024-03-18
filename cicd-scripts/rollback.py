#!/usr/bin/env python
"""This program provides rollback job actions."""

# Import standard module
from typing import cast

# Import project modules
from utils import CICDAction, CICDStep, helm


class RollbackStep(CICDStep):
    """This class provides rollback support."""

    def rollback_ansible(self) -> None:
        """Run an Ansible rollback."""
        self.run_ansible_playbook()

    def rollback_helm(self) -> None:
        """Rollback method for Helm charts."""
        chart_name = self.step_info.chart_name if self.step_info.chart_name else self.project.product.lower()
        helm('rollback',
             self.step_info.release_name.lower() if self.step_info.release_name else chart_name,
             wait=True, **self.helm_args)

    def rollback_qb(self) -> None:
        """Rollback a QuickBuild deploy."""
        self.qb_deploy(rollback=True)


def main() -> None:
    """This is the main entry point."""
    CICDAction('rollback', cast(CICDStep, RollbackStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore cicd kubeconfig
