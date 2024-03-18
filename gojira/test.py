"""This module provides test actions."""

# Import standard modules
from pathlib import Path
from typing import cast

# Import third-party-modules
from batcave.fileutil import slurp
from batcave.sysutil import rmpath, syscmd
from yaml import full_load as yaml_load

# Import project modules
from .utils import DEFAULT_ENCODING, GojiraAction, GojiraStep, helm


class TestStep(GojiraStep):
    """This class provides test support."""

    def pre(self) -> None:
        """Prepare for testing on first run."""
        super().pre()
        if self.step_info.is_first_step:
            self.log_message('Preparing test results directory', True)
            if Path(self.project.test_results_dir).exists():
                self.log_message(f'Removing test results directory: {self.project.test_results_dir}')
                rmpath(self.project.test_results_dir)
            if not Path(self.project.test_results_dir).exists():
                self.log_message(f'Creating clean test results directory: {self.project.test_results_dir}')
                Path(self.project.test_results_dir).mkdir(parents=True)

    def test_docker(self) -> None:
        """Lint method for Docker dockerfiles."""
        dockerfile = slurp(self.dockerfile)
        syscmd('docker', 'run', '--interactive', '--rm', 'hadolint/hadolint', input_lines=dockerfile, ignore_stderr=True)
        if self.step_info.build_test_stage:
            self.docker_build(target=self.step_info.build_test_stage)

    def test_helm(self) -> None:
        """Lint method for Helm charts."""
        helm('dependency', 'build', self.helm_chart_root)
        helm('lint', self.helm_chart_root, **self.helm_args)
        with open(self.helm_chart_root / 'Chart.yaml', encoding=DEFAULT_ENCODING) as yaml_stream:
            helm_info = yaml_load(yaml_stream)
        if helm_info['type'] != 'library':
            helm('template', self.helm_chart_root, **self.helm_args)


def test() -> None:
    """This is the main entry point."""
    GojiraAction('test', cast(GojiraStep, TestStep)).execute()

# cSpell:ignore batcave fileutil syscmd hadolint dockerfiles gojira
