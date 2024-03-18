#!/usr/bin/env python3
"""This is the bootstrap program for running the Gojira actions.
Since this program can be called before the requirements are install, it can only import standard modules.
"""

# Import standard modules
from importlib import import_module
from os import getenv, putenv
from sys import argv, exit as sys_exit, stderr, version as python_version

# Import local modules
from .utils import apt, apt_install, pip_install, pip_setup

ENV_VARS = {'_BUILD_ARTIFACTS': 'artifacts',
            '_TEST_RESULTS': 'test_results',
            '_GCP_ARTIFACT_REGION': 'us',
            '_GCP_ARTIFACT_REPO': 'cysiv-deployment-pipeline',
            '_DOCKER_REPO_NAME': 'gcr.io',
            '_DOCKER_REPO': '{_GCP_ARTIFACT_REGION}-docker.pkg.dev/{_GCP_ARTIFACT_REPO}/{_DOCKER_REPO_NAME}',
            '_HELM_REPO_NAME': 'forescout-helm-repo',
            '_HELM_REPO': 'oci://{_GCP_ARTIFACT_REGION}-docker.pkg.dev/{_GCP_ARTIFACT_REPO}/{_HELM_REPO_NAME}'}

ACTIONS = ['test', 'build', 'deploy', 'rollback', 'pre_release', 'release']


def main() -> None:
    """The main entrypoint."""
    if len(argv) == 1:
        print('usage:', argv[0], 'action ...', file=stderr)
        sys_exit(1)
    actions = argv[1:]

    env_vars = {}
    for (var, default) in ENV_VARS.items():
        if (value := getenv(var)) is None:
            value = default
        env_vars[var] = value
    for (var, value) in env_vars.items():
        putenv(var, value.format(**env_vars))

    if getenv('_CICD_ENV', '') == 'dev-user':
        if not getenv('VIRTUAL_ENV', ''):
            print('This must be run from a virtual environment.', file=stderr)
            sys_exit(1)
    else:
        putenv('GIT_PYTHON_REFRESH', 'quiet')
        with open('/etc/os-release', encoding='utf8') as release_file:
            for line in release_file:
                print(line)
        print(f'Python version: {python_version}')

    unknown_actions = set(actions) - set(ACTIONS)
    if unknown_actions:
        print('Unknown actions requested:', ','.join(unknown_actions))
        sys_exit(1)

    _initialize()
    for action in actions:
        action_module = import_module(f'.{action}')
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

# cSpell:ignore putenv gojira
