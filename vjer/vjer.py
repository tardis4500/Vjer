#!/usr/bin/env python3
"""This is the bootstrap program for running the Vjer actions.
Since this program can be called before the requirements are install, it can only import standard modules.
"""

# Import standard modules
from importlib import import_module
import os
from os import getenv
from platform import platform
from sys import exit as sys_exit, stderr, version as python_version

# Import third-party modules
from batcave.commander import Argument, Commander

# Import local modules
from .utils import apt, apt_install, VJER_ENV, pip_install, ProjectConfig, ConfigurationError, PROJECT_CFG_FILE

ACTIONS = ['test', 'build', 'deploy', 'rollback', 'pre_release', 'release', 'freeze']


def main() -> None:
    """The main entrypoint."""
    args = Commander('Vjer CI/CD Automation Tool', [Argument('actions', choices=ACTIONS, nargs='+')]).parse_args()
    _setup_environment()
    print(f'OS: {platform()}\nPython version: {python_version}')

    _sys_initialize()
    for action in args.actions:
        action_module = import_module(f'vjer.{action}')
        action_module.__dict__[action]()


def _pip_setup() -> None:
    pip_install('pip')
    pip_install('setuptools', 'wheel')


def _setup_environment() -> None:
    try:
        config = ProjectConfig()
    except ConfigurationError as err:
        if err.code != ConfigurationError.CONFIG_FILE_NOT_FOUND.code:
            raise
        print('The Vjer configuration file was not found:', PROJECT_CFG_FILE, file=stderr)
        sys_exit(1)
    if (VJER_ENV == 'local') and not getenv('VIRTUAL_ENV', ''):
        print('Vjer must be run from a virtual environment.', file=stderr)
        sys_exit(1)
    if hasattr((config := ProjectConfig()).project, 'environment'):
        for (var, val) in config.project.environment.items():
            print(f'setting {var}={val}')
            os.environ[var] = val  # putenv doesn't work because the values are needed for this process.


def _sys_initialize() -> None:
    if pkg_installs := getenv('VJER_PKG_INSTALLS', ''):
        apt('update')
        apt_install(pkg_installs)

    if (pip_installs := getenv('VJER_PIP_INSTALLS', '')) or (pip_file := getenv('VJER_PIP_INSTALL_FILE', '')):
        _pip_setup()
        if pip_installs:
            pip_install(pip_installs)
        if pip_file:
            pip_install(requirement=pip_file)


if __name__ == '__main__':
    main()

# cSpell:ignore batcave vjer fileutil syscmd putenv
