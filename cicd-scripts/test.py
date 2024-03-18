#!/usr/bin/env python
"""This program provides test job actions."""

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
from utils import DEFAULT_ENCODING, CICDAction, CICDStep, helm


class TestStep(CICDStep):
    """This class provides test support."""

    def pre(self) -> None:
        super().pre()
        if self.step_info.is_first_step:
            self.log_message('Preparing test results directory', True)
            if Path(self.project.test_results_dir).exists():
                self.log_message(f'Removing test results directory: {self.project.test_results_dir}')
                rmpath(self.project.test_results_dir)
            if not Path(self.project.test_results_dir).exists():
                self.log_message(f'Creating clean test results directory: {self.project.test_results_dir}')
                Path(self.project.test_results_dir).mkdir(parents=True)

    def test_ansible(self) -> None:
        """Lint method for Ansible playbooks."""
        SysCmdRunner('ansible-lint', Path(self.ansible_dir, self.playbook), syscmd_args={'ignore_stderr': True}).run()

    def test_docker(self) -> None:
        """Lint method for Docker dockerfiles."""
        dockerfile = slurp(self.dockerfile)
        syscmd('docker', 'run', '--interactive', '--rm', 'hadolint/hadolint', input_lines=dockerfile, ignore_stderr=True)

    def test_flake8(self) -> None:
        """Run python flake8 linter."""
        SysCmdRunner('flake8', *self.step_info.targets, **self.step_info.flake8_args).run()

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
        SysCmdRunner('mypy', *self.step_info.targets, **self.step_info.mypy_args).run()

    def test_pylint(self) -> None:
        """Run python pylint linter."""
        SysCmdRunner('pylint', *self.step_info.targets, **self.step_info.pylint_args).run()

    def test_python_unittest(self) -> None:
        """Runs the Python unittest module framework."""
        XMLTestRunner(output=str(self.project.test_results_dir), failfast=True, verbosity=2).run(defaultTestLoader.discover(self.project.project_root))
        for junit_results in self.project.test_results_dir.iterdir():
            test_suite = JUnitXml.fromfile(str(junit_results))
            if test_suite.errors or test_suite.failures:
                print('Unit tests failed', file=stderr)
                sys_exit(1)
            junit_results.rename(junit_results.parent / f'junit-{junit_results.name}')


def main() -> None:
    """This is the main entry point."""
    CICDAction('test', cast(CICDStep, TestStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore batcave cicd fileutil junitparser hadolint syscmd xmlrunner dockerfiles
