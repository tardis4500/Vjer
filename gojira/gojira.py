#!/usr/bin/env python3
"""This is the bootstrap program for running the Gojira actions.
Since this program can be called before the requirements are install, it can only import standard modules.
"""

# Import standard modules
from importlib import import_module
from os import getenv, putenv
from sys import exit as sys_exit, stderr, version as python_version

# Import third-party modules
from batcave.commander import Argument, Commander

# Import local modules
from .utils import apt, apt_install, pip_install, pip_setup

ACTIONS = ['test', 'build', 'deploy', 'rollback', 'pre_release', 'release', 'freeze']
ENV_VARS = {'_BUILD_ARTIFACTS': 'artifacts',
            '_TEST_RESULTS': 'test_results',
            '_GCP_ARTIFACT_REGION': 'us',
            '_DOCKER_REPO': '{_GCP_ARTIFACT_REGION}-docker.pkg.dev/{_GCP_ARTIFACT_REPO}/{_DOCKER_REPO_NAME}',
            '_HELM_REPO': 'oci://{_GCP_ARTIFACT_REGION}-docker.pkg.dev/{_GCP_ARTIFACT_REPO}/{_HELM_REPO_NAME}'}


def main() -> None:
    """The main entrypoint."""
    args = Commander('Gojira CI/CD Automation Tool', [Argument('action', choices=ACTIONS)]).parse_args()
    actions = [args.action]

    env_vars = {}
    for (var, default) in ENV_VARS.items():
        if (value := getenv(var)) is None:
            value = default
        env_vars[var] = value
    for (var, value) in env_vars.items():
        putenv(var, value.format(**env_vars))

    if getenv('GOJIRA_ENV', '') == 'local':
        if not getenv('VIRTUAL_ENV', ''):
            print('This must be run from a virtual environment.', file=stderr)
            sys_exit(1)
    else:
        putenv('GIT_PYTHON_REFRESH', 'quiet')
        with open('/etc/os-release', encoding='utf8') as release_file:
            for line in release_file:
                print(line)
        print(f'Python version: {python_version}')

    _initialize()
    for action in actions:
        action_module = import_module(f'gojira.{action}')
        action_module.__dict__[action]()


def _initialize() -> None:
    if pkg_installs := getenv('_PKG_INSTALLS', ''):
        apt('update')
        apt_install(pkg_installs)

    if (pip_installs := getenv('_PIP_INSTALLS', '')) or (pip_file := getenv('_PIP_INSTALL_FILE', '')):
        pip_setup()
        if pip_installs:
            pip_install(pip_installs)
        if pip_file:
            pip_install(requirement=pip_file)


if __name__ == '__main__':
    main()

# cSpell:ignore batcave putenv gojira
