"""This module provides test actions."""

# Import standard modules
from pathlib import Path
from sys import exit as sys_exit, stderr
from typing import cast
from unittest import defaultTestLoader

# Import third-party-modules
from batcave.fileutil import slurp
from batcave.sysutil import rmpath, syscmd, SysCmdRunner
from junitparser import JUnitXml
from xmlrunner import XMLTestRunner
from yaml import full_load as yaml_load

# Import project modules
from .utils import DEFAULT_ENCODING, VjerAction, VjerStep, helm


class TestStep(VjerStep):
    """This class provides test support."""

    def _test_runner(self, test_name: str) -> None:
        """Run tester."""
        SysCmdRunner(test_name, *(self.step_info.targets if self.step_info.targets else [self.project.name]), **self.step_info.options).run()

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

    def test_flake8(self) -> None:
        """Run python flake8 linter."""
        self._test_runner('flake8')

    def test_helm(self) -> None:
        """Lint method for Helm charts."""
        helm('dependency', 'build', self.helm_chart_root)
        helm('lint', self.helm_chart_root, **self.helm_args)
        with open(self.helm_chart_root / 'Chart.yaml', encoding=DEFAULT_ENCODING) as yaml_stream:
            helm_info = yaml_load(yaml_stream)
        if helm_info['type'] != 'library':
            helm('template', self.helm_chart_root, **self.helm_args)

    def test_mypy(self) -> None:
        """Run python mypy linter."""
        self._test_runner('mypy')

    def test_pylint(self) -> None:
        """Run python pylint linter."""
        self._test_runner('pylint')

    def test_python_unittest(self) -> None:
        """Runs the Python unittest module framework."""
        XMLTestRunner(output=str(self.project.test_results_dir), failfast=True, verbosity=2).run(defaultTestLoader.discover(self.project.project_root))
        for junit_results in self.project.test_results_dir.iterdir():
            test_suite = JUnitXml.fromfile(str(junit_results))
            if test_suite.errors or test_suite.failures:
                print('Unit tests failed', file=stderr)
                sys_exit(1)
            junit_results.rename(junit_results.parent / f'junit-{junit_results.name}')


def test() -> None:
    """This is the main entry point."""
    VjerAction('test', cast(VjerStep, TestStep)).execute()

# cSpell:ignore batcave fileutil syscmd hadolint dockerfiles vjer junitparser xmlrunner
