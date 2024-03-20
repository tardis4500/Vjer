"""This module provides deployment rollback actions."""

# Import standard module
from typing import cast

# Import project modules
from .utils import VjerAction, VjerStep, helm


class RollbackStep(VjerStep):
    """This class provides rollback support."""

    def rollback_helm(self) -> None:
        """Rollback method for Helm charts."""
        chart_name = self.step_info.chart_name if self.step_info.chart_name else self.project.product.lower()
        helm('rollback',
             self.step_info.release_name.lower() if self.step_info.release_name else chart_name,
             wait=True, **self.helm_args)


def rollback() -> None:
    """This is the main entry point."""
    VjerAction('rollback', cast(VjerStep, RollbackStep)).execute()

# cSpell:ignore vjer
