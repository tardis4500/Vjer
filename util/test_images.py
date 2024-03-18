"""This program is used to test BaRT images."""

# Import standard modules
import os
from os import getlogin
from pathlib import Path
from sys import exit as sys_exit, stderr

# Import third-party modules
from batcave.cms import Client, ClientType
from batcave.commander import Argument, Commander
from batcave.lang import dotmap_to_yaml, yaml_to_dotmap
from batcave.fileutil import slurp, spew
from batcave.sysutil import rmpath, popd, pushd
from dotmap import DotMap
from requests import post

os.environ['CI_API_V4_URL'] = 'https://gitlab.buildone.co/api/v4'

DEPLOY_FILE = Path('release-definition.yml')
PIPELINE_FILE = Path('.gitlab-ci.yml')
TEST_BRANCH = 'bart-testing'
TEST_BRANCH_PREFIX = DotMap(SRECleaner='feature', SRECleanerDeployer='release', default=getlogin())
TOKEN_FILE = Path('~/.ssh/bart-testing-pipeline-tokens.yml ').expanduser()

PROJECTS = DotMap(SRECleaner=DotMap(repo='git@gitlab.buildone.co:cc/sre/srecleaner.git', branch='main', gitlab_id=674, disable_pipeline_trigger=True),
                  SRECleanerDeployer=DotMap(repo='git@gitlab.buildone.co:deployers/srecleanerdeployer.git', branch='main', gitlab_id=736, disable_pipeline_trigger=True, deployer='SRECleaner'),
                  ExportAgent=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/export.git', branch='development', gitlab_id=269),
                  PPR_BE=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/project-plan-room.git', branch='rc', gitlab_id=732),
                  PPR_UI=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/ppr.git', branch='trunk', gitlab_id=733),
                  AdminPortal_BE=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/admin-portal/ccs.adminportal.git', branch='develop', gitlab_id=852),
                  AdminPortal_UI=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/admin-portal/adminportal-frontend.git', branch='develop', gitlab_id=398),
                  UI_Component_Library=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/ui-component-library.git', branch='master', gitlab_id=395),
                  Entitlements=DotMap(repo='git@gitlab.buildone.co:product-development/cc-platform/CCS.Entitlements.git', branch='develop', gitlab_id=110))


def main() -> None:
    """Main entry point."""
    args = Commander('BaRT Image Tester', [Argument('-r', '--release'), Argument('branch'), Argument('project', choices=list(PROJECTS.keys()))]).parse_args()
    project_info = PROJECTS[args.project]
    if project_info.deployer and not args.release:
        print('A deployer test requires the --release argument', file=stderr)
        sys_exit(1)
    pipeline_token = yaml_to_dotmap(TOKEN_FILE)[args.project]
    test_branch = TEST_BRANCH_PREFIX.get(args.project, TEST_BRANCH_PREFIX.default) + f'/{TEST_BRANCH}'
    test_dir = None
    try:
        with Client(ClientType.git, 'bart-test', connect_info=project_info.repo, branch=project_info.branch, cleanup=False) as cms_client:
            pushd(test_dir := cms_client.root)
            cms_client.switch(test_branch)
            spew(PIPELINE_FILE, [f'    ref: {args.branch}\n' if 'ref:' in line else line for line in slurp(PIPELINE_FILE)])
            git_files = [PIPELINE_FILE]
            if project_info.deployer:
                git_files.append(DEPLOY_FILE)
                release_definition = yaml_to_dotmap(DEPLOY_FILE)
                release_definition[project_info.deployer].version = args.release
                dotmap_to_yaml(release_definition, DEPLOY_FILE)
            cms_client.checkout_files(*git_files)
            cms_client.checkin_files('BaRT testing')
            if not project_info.disable_pipeline_trigger:
                post(f'https://gitlab.buildone.co/api/v4/projects/{project_info.gitlab_id}/trigger/pipeline',
                     data={'ref': test_branch, 'token': pipeline_token},
                     verify=False, timeout=60).raise_for_status()
    finally:
        popd()
        if test_dir:
            try:
                rmpath(test_dir)
            except PermissionError:
                print('Unable to remove repo clone:', test_dir, file=stderr)


if __name__ == '__main__':
    main()

# cSpell:ignore batcave srecleaner getlogin checkin fileutil dotmap glptt adminportal srecleanerdeployer
