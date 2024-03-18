"""Module to hold common values and utility functions for CI/CD support scripts.

Attributes:
    TITLE (str): The project title which is set during the build.
    VERSION (str): The project version which is set during the build.
    BUILDNAME (str): The build name which is set during the build.
    BUILDDATE (str): The build date which is set during the build.
    PACKAGE_BUCKET (str): The name of the JFrog Artifactory bucket where packages are stored.
    PKG_EXT (str): The extension of a generic package.
    PROJECT_CFG_VAR (str): The environment variable used to specify a non-default project config file.
    PROJECT_CFG_FILE (str): The name of the project config file.
    TOOL_REPORT (Path): The path of the tool report.

    RELEASE_PRE_STEPS (list): The list of release steps to perform before the ones specified for the project.
    RELEASE_POST_STEPS (list): The list of release steps to perform before the ones specified for the project.

    QB_Env (Enum): The list of QuickBuild environments.
    QB_ENV_MAP (DotMap): A mapping of QuickBuild source to target environments.

    There are several tool runners defined for simplified usage: ansible, dotnet, git, helm.
"""
# pylint: disable=too-many-lines

# Import standard modules
from copy import deepcopy as copy_object
from datetime import datetime
from enum import Enum
from os import getenv
from pathlib import Path
from random import randint
from shutil import copy, copytree
from string import Template
from sys import exit as sys_exit, stderr, stdout
from tempfile import mkdtemp
from typing import Callable, cast, Optional
from xml.etree.ElementTree import ParseError

# Import third-party modules
from batcave.automation import Action
from batcave.cloudmgr import gcloud, Cloud, CloudType
from batcave.cms import Client, ClientType
from batcave.expander import Expander
from batcave.fileutil import pack, unpack
from batcave.lang import BatCaveError, BatCaveException, PathName, DEFAULT_ENCODING, WIN32, yaml_to_dotmap
from batcave.platarch import Platform
from batcave.qbpy import QuickBuildBuild, QuickBuildCfg, QuickBuildConsole
from batcave.sysutil import CMDError, SysCmdRunner, popd, pushd, rmpath, syscmd
from dicttoxml import dicttoxml
from dotmap import DotMap
import requests
from requests import codes, Response
from yaml import safe_dump as yaml_dump, safe_load as yaml_load
from xmltodict import parse as xml_parse

# Import project modules
from tool_report import tool_reporter

_CONFIG_SECTIONS = ('project', 'test', 'build', 'deploy', 'rollback', 'release')
_VALID_SCHEMAS = [1]

_DEFAULTS = DotMap(ansible_dir='ansible',
                   chart_repo=DotMap(name='coco-oc',
                                     type='jfrog',
                                     push_url=getenv('HELM_PUSH_REPO'),
                                     push_args=DotMap(username=getenv('JFROG_USER_LOGIN'), password=getenv('JFROG_USER_TOKEN'))),
                   chart_root='helm-chart',
                   container_registry=DotMap(name=getenv('DOCKER_PUSH_REPO'),
                                             type='jfrog',
                                             pull_host=getenv('CC_DOCKER_REGISTRY'),
                                             push_url=getenv('ARTIFACTORY_URL', '').replace('/artifactory', ''),
                                             auth=[getenv('JFROG_USER_LOGIN'), getenv('JFROG_USER_TOKEN')]),
                   dockerfile='Dockerfile',
                   playbook='playbook.yml')

TITLE = '{var:product}'
VERSION = '{var:version}'
BUILDNAME = '{var:build_name}'
BUILDDATE = '{var:build_date}'
PACKAGE_BUCKET = 'bart-published-files'
PKG_EXT = '.tar.xz'
PROJECT_CFG_VAR = 'PROJECT_CFG'
PROJECT_CFG_FILE = getenv(PROJECT_CFG_VAR, 'project-cfg.yml')
TOOL_REPORT = Path(__file__).parent.absolute() / 'tool_report.yml'

RELEASE_PRE_STEPS = ['tag_source']
RELEASE_POST_STEPS = ['gitlab', 'increment_release']

QB_Env = Enum('QB_Env', ('QA', 'Staging', 'Staging2', 'Production', 'Production2', 'InternalProd', 'DR'))
QB_ENV_MAP = DotMap(default=QB_Env.Staging, Staging=QB_Env.QA)

ansible = SysCmdRunner('ansible-playbook', syscmd_args={'ignore_stderr': True, 'append_stderr': True}).run
dotnet = SysCmdRunner('dotnet').run
git = SysCmdRunner('git').run
helm = SysCmdRunner('helm', syscmd_args={'ignore_stderr': True}).run


class ConfigurationError(BatCaveException):
    """Configuration errors.

    Attributes:
        BAD_FORMAT: The format of the configuration file is bad.
        CONFIG_FILE_NOT_FOUND: The config file was not found.
        INVALID_SCHEMA: The schema of the configuration file is not supported.
    """
    BAD_FORMAT = BatCaveError(1, Template('Invalid format for configuration file: $file'))
    CONFIG_FILE_NOT_FOUND = BatCaveError(2, Template('Configuration file not found: $file'))
    INVALID_SCHEMA = BatCaveError(3, Template('Invalid configuration schema: found=$found, expected=$expected'))


class StepError(BatCaveException):
    """Step errors.

    Attributes:
        ANSIBLE_ERROR: There was an error when running an Ansible playbook.
        DUPLICATE_PUBLISH: The published archive already exists.
        REMOTE_FILE_NOT_FOUND: The remote file was not found.
        UNKNOWN_OBJECT: The specified object is of an unknown type.
    """
    ANSIBLE_ERROR = BatCaveError(1, Template('Error running Ansible playbook: $msg'))
    DUPLICATE_PUBLISH = BatCaveError(2, Template('Published archive already exists: $archive'))
    REMOTE_FILE_NOT_FOUND = BatCaveError(3, Template('Unable to locate remote file: $file'))
    UNKNOWN_OBJECT = BatCaveError(4, Template('Unknown $type: $name'))


class Environment:  # pylint: disable=too-few-public-methods
    """Provides an interface to the environment variables."""

    def __getattr__(self, attr: str):
        value = getenv(attr)
        if value is None:
            raise AttributeError(f'Environment variable not found: {attr}')
        return value


class GitLab(Environment):  # pylint: disable=too-many-instance-attributes
    """Provides an interface to the GitLab server environment and API."""

    def __init__(self, project_id: Optional[str] = None, client_root: Optional[PathName] = None, branch: Optional[str] = None):
        """
        Args:
            project_id (optional, default=None): The ID of the GitLab project.
            client_root (optional, default=None): The root directory of the project.
            branch (optional, default=None): The branch to use for the Git client.

        Attributes:
            CI_API_URL: The GitLab API URL.
            CI_ARTIFACTS_URL: The full GitLab URL to the project.
            CI_GENERIC_PACKAGE_URL: The GitLab generic package API URL.
            CI_PACKAGE_URL: The GitLab package API URL.
            CI_PROJECT_API_URL: The GitLab project API URL.
            CI_PROJECT_PATH: The full GitLab project path.
            CI_PYPI_URL: The GitLab PyPi package API URL.
            CI_RELEASES_API: The GitLab release API URL.
            CI_REMOTE_REF: The full git reference to the project.
            branch: The value of the branch argument.
            client: The git client for the project.
            project_id: The value of the project_id argument.
        """
        # pylint: disable=invalid-name
        if hasattr(self, 'CI_PROJECT_NAMESPACE') and hasattr(self, 'CI_PROJECT_NAME'):
            self.CI_PROJECT_PATH = f'{self.CI_PROJECT_NAMESPACE}/{self.CI_PROJECT_NAME}'
            if hasattr(self, 'CI_SERVER_URL'):
                self.CI_ARTIFACTS_URL = f'{self.CI_SERVER_URL}/{self.CI_PROJECT_PATH}'
            if hasattr(self, 'CI_SERVER_HOST'):
                self.CI_REMOTE_REF = f'https://{self.GITLAB_USER_LOGIN}:{self.GITLAB_USER_TOKEN}@{self.CI_SERVER_HOST}/{self.CI_PROJECT_PATH}.git'
            if hasattr(self, 'CI_API_V4_URL'):
                self.CI_API_URL = self.CI_API_V4_URL
            self.CI_PROJECT_API_URL = f'{self.CI_API_URL}/projects'
            self.CI_RELEASES_API = f'{self.CI_PROJECT_API_URL}/{self.CI_PROJECT_PATH.replace("/", "%2F")}/releases'
            self.CI_PACKAGE_URL = f'{self.CI_PROJECT_API_URL}/{self.CI_PROJECT_ID}/packages'
            self.CI_GENERIC_PACKAGE_URL = f'{self.CI_PACKAGE_URL}/generic'
            self.CI_PYPI_URL = f'{self.CI_PACKAGE_URL}/pypi'
        # pylint: enable=invalid-name
        self.project_id = project_id
        self.client = Client(ClientType.git, 'bart', connect_info=str(client_root), create=False) if (client_root and (Path(client_root) / '.git').exists()) else None
        self.branch = branch if branch else getattr(self, 'CI_COMMIT_BRANCH', '')

    def __enter__(self):
        return self

    def __exit__(self, *_unused_exc_info):
        return False

    def _call_gitlab_api(self, call_type: str, object_type: str, object_id: str = '', sub_object_type: str = '', /, *, query: str = '') -> str | dict:  # pylint: disable=too-many-arguments
        """Call the GitLab API.

        Args:
            call_type: The API call type.
            object_type: The object type for the call.
            object_id (optional, default=None): The object ID for the call.
            sub_object_type (optional, default=None): The sub object type for the call.
            query (optional, default=None): The query for the call.

        Returns:
            The response from the API call.
        """
        api_call = f'{self.CI_PROJECT_API_URL}/{self.project_id}/{object_type}'
        if object_id:
            api_call += f'/{object_id}'
        if sub_object_type:
            api_call += f'/{sub_object_type}'
        if query:
            api_call += f'?{query}'

        (response := getattr(requests, call_type)(api_call, headers={'Private-Token': getenv('GITLAB_USER_TOKEN')}, timeout=60)).raise_for_status()
        return response.text if (sub_object_type == 'raw') else response.json()

    @property
    def cicd_cfg(self) -> DotMap:
        """A read-only property which returns the CI/CD pipeline file."""
        return self.get_file('.gitlab-ci.yml')

    @property
    def latest_jobs(self) -> list:
        """A read-only property which returns the latest pipeline job list."""
        return cast(list, self._call_gitlab_api('get', 'pipelines', self.latest_pipeline['id'], 'jobs'))

    @property
    def latest_pipeline(self) -> dict:
        """A read-only property which returns the latest pipeline."""
        return cast(dict, self._call_gitlab_api('get', 'pipelines', query=f'ref={self.branch}'))[0]

    @property
    def latest_build_num(self) -> str:
        """A read-only property which returns the latest build number."""
        return self.latest_pipeline['iid']

    @property
    def project_cfg(self) -> DotMap:
        """A read-only property which returns the project config file."""
        return self.get_file(PROJECT_CFG_FILE)

    def get_file(self, filename: str, /) -> DotMap:
        """Get the contents of the file as a DotMap.

        Args:
            filename: The file name to read.

        Returns:
            The contents of the file as a DotMap.
        """
        return yaml_to_dotmap(str(self._call_gitlab_api('get', 'repository/files', filename, 'raw', query=f'ref={self.branch}')))

    def run_job(self, name: str, /, *, wait: bool = True) -> dict:
        """Run a pipeline job.

        Args:
            name: The name of the job to run.
            wait (optional, default=True): If True, wait for the job to finish before returning.

        Returns:
            The result of the job run.
        """
        last_job_status = last_job_id = ''
        for job in self.latest_jobs:
            if job['name'] == name:
                last_job_id = job['id']
                last_job_status = job['status']
                break
        action = 'play' if (last_job_status == 'manual') else 'retry'
        new_job_id: str = cast(dict, self._call_gitlab_api('post', 'jobs', last_job_id, action))['id']
        while result := cast(dict, self._call_gitlab_api('get', 'jobs', new_job_id)):
            if not wait:
                return result
            if result['status'] not in ('created', 'pending', 'running'):
                break
        return cast(dict, result)


class ConfigSection():
    """Base class to manage configuration sections."""

    def __init__(self, **defaults):
        """
        Args:
            **defaults: The default items for the configuration.

        Attributes:
            _default_property_holders: A list of property holders for defaults.
            _defaults: The configuration defaults.
            _expander: The expander to use for variable replacement.
            _values: The configuration values.
        """
        self._values = DotMap()
        self._defaults = DotMap(**defaults)
        self._default_property_holders = [Environment()]
        self._expander = None
        self.update_expander(property_holders=self._default_property_holders)

    def __getattr__(self, attr: str):
        for config in (self._values, self._defaults):
            if attr in config:
                value = getattr(config, attr)
                if isinstance(value, list):
                    return [self._expander.expand(v) for v in value]
                if isinstance(value, dict):
                    return {k: self._expander.expand(v) for (k, v) in value.items()}
                if isinstance(value, str):
                    return self._expander.expand(value)
                return value
        raise AttributeError(f'No configuration value found: {attr}')

    def __setattr__(self, attr: str, value: str):
        if attr.startswith('_'):
            super().__setattr__(attr, value)
            return
        setattr(self._values, attr, value)

    values = property(lambda s: s._values.toDict(), doc='A read-only property which returns the configuration values.')

    def update_expander(self, *, property_holders: Optional[list] = None, property_dict: Optional[dict] = None) -> None:
        """Set the expander property holders.

        Args:
            property_holders (optional, default=None): A list of property holders from which to read values.
            property_dict (optional, default=None): A dictionary from which to read values.

        Returns:
            Nothing.
        """
        if property_holders:
            self._expander = Expander(var_props=property_holders + self._default_property_holders)
        if property_dict:
            self._expander.var_dict |= property_dict

    def update(self, values: dict, /) -> None:
        """Update the configuration section values.

        Args:
            values: Update the configuration values from the provided dictionary.

        Returns:
            Nothing.
        """
        self._values |= values

    def update_defaults(self, values: dict, /) -> None:
        """Updates the configuration section default values.

        Args:
            values: Update the defaults with the provided dictionary.

        Returns:
            Nothing.
        """
        self._defaults |= values


class ProjectConfig():
    """Stores project related configuration items."""

    def __init__(self):  # pylint: disable=too-many-branches,too-many-locals
        """
        Attributes:
            _config_file: The config file for the project configuration.
            _sections: A list of the sections in the project configuration.
            schema: The schema version of the project configuration.
            use_steps: A dictionary of steps by section.
        """
        project_root = Path.cwd()
        gitlab = GitLab()
        self._sections = {'project': ConfigSection(project_root=project_root,
                                                   artifacts_dir=project_root / gitlab.CI_BUILD_ARTIFACTS,
                                                   build_num_var='CI_PIPELINE_IID',
                                                   p2_branch=gitlab.branch if (gitlab.branch in ('develop', 'rc')) else 'feature',
                                                   test_results_dir=project_root / gitlab.CI_TEST_RESULTS),
                          'test': ConfigSection(),
                          'deploy': ConfigSection(clean=True),
                          'rollback': ConfigSection(clean=True),
                          'release': ConfigSection()}
        self._sections['build'] = ConfigSection(source_dir=self.project.project_root / 'src',
                                                version_files=[],
                                                artifacts_dir=self.project.project_root / gitlab.CI_BUILD_ARTIFACTS,
                                                artifacts={},
                                                archive_artifacts=False,
                                                build_date=str(datetime.now()),
                                                platform=Platform().bart)
        self._config_file = self.project.project_root / PROJECT_CFG_FILE
        if not self._config_file.exists():
            raise ConfigurationError(ConfigurationError.CONFIG_FILE_NOT_FOUND, file=self._config_file)
        yaml_as_dict = DotMap(schema=0)
        with open(self._config_file, encoding=DEFAULT_ENCODING) as config_file:
            yaml_as_dict |= DotMap(yaml_load(config_file))
        if not yaml_as_dict:
            raise ConfigurationError(ConfigurationError.BAD_FORMAT, file=self._config_file)
        if yaml_as_dict.schema not in _VALID_SCHEMAS:
            raise ConfigurationError(ConfigurationError.INVALID_SCHEMA, found=yaml_as_dict.schema, expected=_VALID_SCHEMAS)
        self.schema = yaml_as_dict.schema

        for section in _CONFIG_SECTIONS:
            if section in yaml_as_dict:
                self._sections[section].update(yaml_as_dict[section])

        if hasattr(self.project, 'version_service'):
            self._set_version_from_service()
        build_num = getenv(self.project.build_num_var, '0')
        build_version = f'{self.project.version}-{build_num}'
        self.build.update_defaults({'build_num': build_num,
                                    'build_version': build_version,
                                    'build_version_msbuild': f'{self.project.version}.{build_num}',
                                    'build_name': f'{self.project.product}_{build_version}'})
        self.release.update_defaults({'release_tag': f'v{self.project.version}'})
        for (piece, index) in {'major': 0, 'minor': 1, 'patch': 2}.items():
            self.project.update_defaults({f'{piece}': self.project.version.split('.', 2)[index]})

        for section in _CONFIG_SECTIONS:
            self._sections[section].update_expander(property_holders=list(self._sections.values()))

        release_steps = [self._get_phase_step('release', s) for s in RELEASE_PRE_STEPS]
        if hasattr(self.release, 'steps'):
            release_steps += [copy_object(s) for s in self.release.steps if s.get('type') not in RELEASE_PRE_STEPS + RELEASE_POST_STEPS]
        release_steps += [self._get_phase_step('release', s) for s in RELEASE_POST_STEPS]
        self.use_steps = {'release': release_steps}

    def __getattr__(self, attr: str):
        if attr not in self._sections:
            raise AttributeError(f'Configuration section not found: {attr}')
        return self._sections[attr]

    def _get_phase_step(self, phase: str, step_type: str) -> DotMap:
        """Get the specified step type for the specified phase.

        Args:
            phase: The phase for which to return the step.
            step_type: The step type to return from the phase.

        Returns:
            A DotMap for the step.
        """
        if hasattr(phase_ref := getattr(self, phase), 'steps'):
            for step in phase_ref.steps:
                if step.get('type') == step_type:
                    return copy_object(step)
        return DotMap(type=step_type)

    def _set_version_from_service(self) -> None:
        """Set the project version from the service specified in the project config.

        Returns:
            Nothing.
        """
        version_service = DotMap(self.project.version_service)
        match version_service.type:
            case 'environment':
                self.project.version = getenv(version_service.variable, '').rstrip('.')
            case 'semver':
                self.project.version = version_service.value
            case _:
                print('Unknown version service:', version_service.type, file=stderr)
                sys_exit(1)

    filename = property(lambda s: s._config_file, doc='A read-only property which returns the configuration file name.')

    def write(self) -> None:
        """Writes out the project configuration.

        Returns:
            Nothing.
        """
        with open(self._config_file, 'w', encoding=DEFAULT_ENCODING) as config_file:
            yaml_dump({'schema': self.schema} | {s: c.values for (s, c) in self._sections.items() if c.values},
                      config_file, indent=2)


class QuickBuildComponent:
    """Represents a QuickBuild product component."""
    _QB_PREFIX = 'ConstructConnect/Environments'

    def __init__(self, console: QuickBuildConsole, component: str):
        """
        Args:
            console: The URL of the QuickBuild console.
            component: The component to load from the QuickBuild console.

        Attributes:
            _component: The value of the component argument.
            _console: The value of the console argument.
        """
        self._console = console
        self._component = component

    def __getattr__(self, attr: str):
        return getattr(self._component, attr)

    def get_cfg(self, environment: QB_Env) -> QuickBuildCfg:
        """Return the QuickBuild configuration for the environment.

        Args:
            environment: The name of the environment for which to return the configuration.

        Returns:
            The QuickBuild configuration.
        """
        return getattr(self._console, f'{self._QB_PREFIX}/{environment.name}/{self.name}')

    def get_latest_build(self, environment: QB_Env) -> Optional[QuickBuildCfg]:
        """Get the latest build for an environment.

        Args:
            environment: The name of the environment for which to return the latest build.

        Returns:
            The QuickBuild build.
        """
        try:
            return cast(Optional[QuickBuildCfg], self.get_cfg(environment).latest_build)
        except ParseError as err:
            if 'no element found' in str(err):
                return None
            raise

    def get_latest_build_num(self, environment: QB_Env) -> str:
        """Get the latest build number for an environment.

        Args:
            environment: The name of the environment for which to return the latest build number.

        Returns:
            The number of the most recent build.
        """
        if not (latest_build := self.get_latest_build(environment)):
            return ''
        return str(latest_build.version).split('_')[2]

    @property
    def rollback_build(self) -> Optional[QuickBuildBuild]:
        """A read-only property which returns the rollback build for the component."""
        rollback_build_prefix = '_'.join(str(cast(QuickBuildCfg, self.get_latest_build(QB_Env.Staging)).version).
                                         replace(f'_{self.build_num}_', f'_{self.rollback_build_num}_').
                                         replace(QB_Env.Staging.name, QB_Env.Production.name).
                                         split('_')[0:-1])
        rollback_cfg = self.get_cfg(QB_Env.Production)
        rollback_build_list = xml_parse(self._console.qb_runner(f'builds?configuration_id={rollback_cfg.id}&version={rollback_build_prefix}_*&count=1').text)['list']
        if not rollback_build_list:
            return None
        return QuickBuildBuild(self._console, rollback_build_list['com.pmease.quickbuild.model.Build']['id'])

    def promote_build(self, source_build: str, source_env: QB_Env, target_env: QB_Env) -> str:
        """Promotes a build to the target environment.

        Args:
            source_build: The name of the source build for which to run the promotion.
            source_env: The name of the source environment for which to run the promotion.
            target_env: The name of the target environment for which to run the promotion.

        Returns:
            The build status.
        """
        build_request = dicttoxml(DotMap(configurationId=self.get_cfg(target_env).id,
                                         respectBuildCondition=False,
                                         priority=10,
                                         variables=DotMap(entry=DotMap(string1='Environment_source', string2=source_env.name)),
                                         promotionSource=DotMap(buildId=source_build,
                                                                deliveries=DotMap({'com.pmease.quickbuild.FileDelivery': DotMap(srcPath='artifacts',
                                                                                                                                filePatterns='**,-ConfigLib/**')}))).toDict(),
                                  custom_root='com.pmease.quickbuild.BuildRequest', xml_declaration=False, attr_type=False, return_bytes=False).\
            replace('string1>', 'string>').replace('string2>', 'string>')
        request_id = xml_parse(self._console.qb_runner('build_requests', xml_data=build_request).text)['com.pmease.quickbuild.RequestResult']['requestId']
        qb_build = None
        while not qb_build:
            response = self._console.qb_runner(f'ids?request_id={request_id}')
            qb_build = None if (response.status_code == codes.no_content) else QuickBuildBuild(self._console, response.text)  # pylint: disable=no-member
        build_status = 'RUNNING'
        while build_status == 'RUNNING':
            build_status = qb_build.status
        return build_status

    def promote(self, source_env: QB_Env, target_env: QB_Env) -> str:
        """Promote from the the source to target environment.

        Args:
            source_env: The name of the source environment for which to run the promotion.
            target_env: The name of the target environment for which to run the promotion.

        Returns:
            The result of the build promotion.
        """
        return self.promote_build(cast(QuickBuildCfg, self.get_latest_build(source_env)).id, source_env, target_env)

    def rollback(self, environment: QB_Env) -> str:
        """Rollback the component to the previous build.

        Args:
            environment: The name of the environment to rollback.

        Returns:
            The result of the rollback.
        """
        return self.promote_build(cast(QuickBuildCfg, self.rollback_build).id, environment, environment)


class RemoteStorage:
    """Class to abstract remote storage handling."""

    def __init__(self, bucket: str):
        """
        Args:
            bucket: The name of the remote bucket for the storage.

        Attributes:
            _bucket_host_url: The URL to the remote storage provider.
            _bucket_info_url: The URL to the info for the remote storage bucket.
            _bucket_url: The URL to the remote storage bucket.
        """
        self._bucket_host_url = getenv('ARTIFACTORY_URL')
        self._bucket_info_url = f'{self._bucket_host_url}/api/storage/{bucket}'
        self._bucket_url = f'{self._bucket_host_url}/{bucket}'

    def _call_api(self, method: str, url: str, /, *, check_response: bool = True, **kwargs) -> Response:
        """Make an API call to the remote storage provider.

        Args:
            method: The API call method.
            url: The URL for the API call.
            check_response (optional, default=True): If True, validate the call returned no errors.
            **kwargs (optional, default={}): Any arguments to pass to the API on the call.

        Returns:
            The API call response.
        """
        response = getattr(requests, method)(url, headers={'Authorization': f'Bearer {getenv("JFROG_USER_TOKEN")}'}, timeout=60, **kwargs)
        if check_response:
            response.raise_for_status()
        return response

    def exists(self, object_name: str, /) -> bool:
        """Determine if an object exists in the remote storage.

        Args:
            object_name: The name of the object to find in the remote storage.

        Returns:
            True if the object exists.

        Raises:
            Any errors from the API call other than if the object is not found.
        """
        response = self._call_api('get', f'{self._bucket_info_url}/{object_name}', check_response=False)
        if response.status_code == codes.not_found:  # pylint: disable=no-member
            return False
        response.raise_for_status()
        return True

    def retrieve(self, object_name: str, download_dir: Optional[PathName] = None, /) -> None:
        """Retrieve an object as a local file.

        Args:
            object_name: The name of the object to retrieve.
            download_dir (optional, default=None): The directory to which to download the file. If None, the current directory is used.

        Returns:
            Nothing.
        """
        response = self._call_api('get', f'{self._bucket_url}/{object_name}?skipUpdateStats=true')
        target_file: PathName = object_name
        if download_dir:
            target_file = Path(download_dir) / target_file
        with open(target_file, 'wb') as downloaded_file:
            downloaded_file.write(response.content)

    def store(self, object_name: str, object_source: PathName, /) -> None:
        """Store an object to the remote storage.

        Args:
            object_name: The remote name for the stored object.
            object_source: The local object to store.

        Returns:
            Nothing.
        """
        with open(object_source, 'rb') as object_stream:
            self._call_api('put', f'{self._bucket_url}/{object_name}', data=object_stream)


class CICDStep(Action):  # pylint: disable=too-many-instance-attributes
    """ Class to represent a single Action step."""

    def __init__(self):
        """
        Attributes:
            build: The project build configuration.
            config: The project configuration.
            docker_client: The Docker client.
            gitlab: The GitLab repository for the project.
            image_name: The Docker image name.
            image_tag: The Docker image tag.
            pre_release_num: The pre-release suffix for the project.
            project: The project name.
            registry_client: The Docker image registry.
            release: The release configuration.
            step_info: The step information.
            version_tag: The Docker image version.
        """
        super().__init__()
        self.config = ProjectConfig()
        self.project = self.config.project
        self.build = self.config.build
        self.release = self.config.release
        self.gitlab = GitLab(client_root=self.project.project_root)
        self.step_info = DotMap()
        self.pre_release_num = self.build.build_num
        # Used by Docker builds
        self.registry_client = None
        self.docker_client = None
        self.image_name = ''
        self.version_tag = ''
        self.image_tag = ''

    def __getattr__(self, attr: str):
        if attr not in _DEFAULTS:
            raise AttributeError(f'No such attribute: {attr}')
        return getattr(self.step_info, attr) if getattr(self.step_info, attr) else _DEFAULTS[attr]

    def _docker_init(self, login: bool = True, mode: str = 'pull') -> None:
        """Perform Docker initialization.

        Args:
            login (optional, default=True): If True, login to the Docker image registry.
            mode (optional, default='pull'): The mode for which this initialization will be used.

        Returns:
            Nothing.
        """
        registry = self.container_registry
        registry_name = getattr(registry, f'{mode}_host') if getattr(registry, f'{mode}_host') else registry.name
        self.registry_client = None
        if login and ((mode != 'push') or (registry.type != 'jfrog')):
            self.log_message(f'Logging into container registry: {registry_name}', True)
            match registry.type:
                case 'gcp':
                    self.registry_client = Cloud(CloudType.gcloud, login=False)
                    gcloud('auth', 'activate-service-account', '--key-file', registry.auth, syscmd_args={'ignore_stderr': True})
                    gcloud('auth', 'configure-docker', syscmd_args={'ignore_stderr': True})
                    self.registry_client._client = True  # pylint: disable=protected-access
                case 'jfrog':
                    self.registry_client = Cloud(CloudType.dockerhub, auth=registry.auth + [None, registry_name])
                case _:
                    raise StepError(StepError.UNKNOWN_OBJECT, type='container registry type', name=registry.type)

        self.docker_client = Cloud(CloudType.local)
        registry_name_path = f'{registry_name}/' if self.registry_client else ''
        self.image_name = f'{registry_name_path}{self.step_info.image if self.step_info.image else self.project.product}'
        self.version_tag = f'{self.image_name}:{self.project.version}'
        self.image_tag = f'{self.version_tag}-{self.build.build_num}'.lower()

    def _execute(self) -> None:
        """This method is called by the Action super class when this class's execute method is called."""
        class_name = type(self).__name__.lower().removeprefix('pre').removesuffix('step')
        action_method = f'{class_name}_{self.step_info.type}'
        if not hasattr(self, action_method):
            print(f'No method defined for action type {self.step_info.type} on {class_name}', file=stderr)
            sys_exit(1)
        getattr(self, action_method)()

    helm_chart_root = property(lambda s: Path(s.chart_root), doc='A read-only property which returns the helm chart root.')
    helm_package = property(lambda s: s.project.artifacts_dir / (s.pkg_name.lower() + '.tgz'), doc='A read-only property which returns the helm chart package name.')
    pkg_archive = property(lambda s: s.project.artifacts_dir / (s.pkg_name + PKG_EXT), doc='A read-only property which returns the release package file name.')
    pkg_name = property(lambda s: f'{s.step_info.pkg_name if s.step_info.pkg_name else s.project.product}-{s.project.version}',
                        doc='A read-only property which returns the release package name.')

    @property
    def helm_args(self) -> dict:
        """A read-only property which returns the Helm command arguments."""
        helm_args = self.step_info.helm_args if self.step_info.helm_args else {}
        if self.step_info.values_files:
            helm_args['values'] = ','.join([str(self.project.artifacts_dir / v) for v in self.step_info.values_files])
        if self.step_info.helm_variables:
            helm_args['set'] = ','.join([f'{k}={v}' for (k, v) in self.step_info.helm_variables.items()])
        return helm_args

    @property
    def helm_repo(self) -> DotMap:
        """A read-only property which returns the Helm repo name with a randomized suffix."""
        if self.chart_repo.url and not self.chart_repo.name:
            repo_name = f'bart-{randint(0, 100)}'
            helm('repo', 'add', repo_name, self.chart_repo.url)
            helm('repo', 'update')
            self.chart_repo.name = repo_name
        return self.chart_repo

    def archive_artifacts(self) -> None:
        """Create an archive from the artifacts in the project artifact directory."""
        pushd(self.project.artifacts_dir)
        for file_name in Path.cwd().iterdir():
            if file_name.is_dir():
                self.create_archive(file_name.name + self.step_info.archive_artifacts, [file_name.name])
                self.log_message(f'Removing: {file_name}')
                rmpath(file_name)
        popd()

    def commit_files(self, message: str, branch: str, *files, file_updater: Optional[Callable] = None) -> None:
        """Checkin files during to the source repository."""
        self.gitlab.client.add_remote_ref(remote_ref := 'cicd_origin', self.gitlab.CI_REMOTE_REF, exists_ok=True)
        git('fetch', all=True, syscmd_args={'ignore_stderr': True})
        git('remote', 'update', remote_ref, prune=True, syscmd_args={'ignore_stderr': True})
        git('checkout', '-B', branch, '--track', f'{remote_ref}/{branch}', syscmd_args={'ignore_stderr': True})
        git('pull', remote_ref, branch, syscmd_args={'ignore_stderr': True})
        if file_updater:
            file_updater()
        self.gitlab.client.add_files(*files)
        self.gitlab.client.checkin_files(message, remote=remote_ref, all_branches=False)

    def copy_artifact(self, src: PathName, dest: Optional[str] = None, /) -> None:
        """Helper method to copy artifacts to the location expected by the continuous integration tool.

        Args:
            src: The source of the artifact to copy.
            dest (optional, default=None): The directory to which to copy the artifact.
                                            If not absolute, this will be a subdirectory of the project archive directory.

        Returns:
            Nothing.
        """
        use_dest = self.project.artifacts_dir
        if dest:
            if Path(dest).is_absolute():
                use_dest = Path(dest)
            else:
                use_dest /= dest
        self.log_message(f'Copying "{src}" to "{use_dest}"')
        if not Path(src).is_dir():
            copy(src, use_dest)
            return

        if WIN32:
            try:
                syscmd('robocopy', str(src), str(use_dest), '/S', '/DCOPY:D', '/COPY:D', '/MT', '/R:3', '/W:30', '/TBD', '/NP', '/NFL', show_stdout=True, ignore_stderr=True, append_stderr=True)
            except CMDError as err:
                if err.vars['returncode'] != 1:
                    raise
            return

        copytree(str(src), str(use_dest), dirs_exist_ok=True)

    def jfrog_upload(self) -> None:
        """Upload the artifacts to JFrog."""
        pushd(self.project.artifacts_dir)
        self.create_archive(self.step_info.jfrog_upload.archive, '*', arc_type=self.step_info.jfrog_upload.archive.split('.')[-1], use_tmpdir=True)
        self.publish_package(self.step_info.jfrog_upload.archive, package_bucket=self.step_info.jfrog_upload.bucket)
        Path(self.step_info.jfrog_upload.archive).unlink()
        popd()

    def publish_package(self, package_source: str, package: Optional[str] = None, package_bucket: Optional[str] = PACKAGE_BUCKET, *, exists_ok: bool = False) -> None:
        """Publish to the package repository to remote storage.

        Args:
            package_source: The source of the package to publish.
            package (optional, default=None): The remote package name. If None, the package source name is used.
            package_bucket (optional, default=PACKAGE_BUCKET): The remote storage bucket to use for storage.
            exists_ok (optional, default=False): If True, raise an error if the package already exists in the remote storage.

        Returns:
            Nothing.

        Raises:
            StepError.DUPLICATE_PUBLISH: If the remote package already exists and exists_ok is False.
        """
        pushd(self.project.artifacts_dir)
        package_source_path = Path(package_source).absolute()
        package_path = package_source_path if (not package) else Path(package).absolute()

        remote_storage = RemoteStorage(str(package_bucket))
        if remote_storage.exists(package_path.name) and (not exists_ok):
            raise StepError(StepError.DUPLICATE_PUBLISH, archive=f'{package_bucket}/{package_path.name}')

        self.log_message(f'Publishing {package_path} to {package_bucket}')
        if package_source_path.is_dir():
            pack(package_path, [package_source])
        popd()
        remote_storage.store(package_path.name, package_path)

    def qb_deploy(self, *, rollback: bool = False) -> None:
        """Deploy or rollback multiple QuickBuild components.

        Args:
            rollback (optional, default=False): If True this is a rollback, otherwise it is a deploy.

        Returns:
            Nothing.
        """
        target = QB_Env[self.gitlab.CI_ENVIRONMENT_NAME.capitalize()]
        source_environment = QB_ENV_MAP.get(target.name, QB_ENV_MAP.default)
        console = QuickBuildConsole(self.gitlab.QB_HOST, user=self.gitlab.GITLAB_USER_LOGIN, password=self.gitlab.QB_PASSWORD)
        components = [QuickBuildComponent(console, c) for c in self.step_info.components]

        validation_errors = []
        for component in components:
            print(f'Validating {component.name}')
            source_build_num = component.get_latest_build_num(source_environment)
            if rollback:
                if not component.rollback_build:
                    validation_errors.append(f'{component.name}: unable to locate rollback build number {component.rollback_build_num}')
            elif str(source_build_num) != str(component.build_num):
                validation_errors.append(f'{component.name}: build number {component.build_num} requested but {source_build_num} found in {source_environment.name}')

        if validation_errors:
            print('Exiting on failed validation:', file=stderr)
            for error in validation_errors:
                print('  ', error, file=stderr)
            sys_exit(1)

        for component in components:
            self.qb_deploy_component(component, source_environment, target, rollback=rollback)
            if target.name in component.extra_environments:
                for extra_env in component.extra_environments[target.name]:
                    self.qb_deploy_component(component, target, QB_Env[extra_env], rollback=rollback)

    def qb_deploy_component(self, component: QuickBuildComponent, source_env: QB_Env, target_env: QB_Env, /, *, rollback: bool) -> None:
        """Deploy or rollback a single QuickBuild component.

        Args:
            component: The component to use.
            source_env: The source environment for the action.
            target_env: The target environment for the action.
            rollback: If True this is a rollback, otherwise it is a deploy.

        Returns:
            Nothing.
        """
        if rollback:
            verb = 'Rolling back'
            method = 'rollback'
            args = [target_env]
            source_build_num = component.rollback_build_num
        else:
            verb = 'Promoting'
            method = 'promote'
            args = [source_env, target_env]
            source_build_num = component.build_num
        promotion_msg = f'{component.name} {source_build_num} to {target_env.name}'
        if target_env.name in component.skip_environments:
            self.log_message(f'Skipping {promotion_msg}...target marked for skipping')
            return
        target_config = component.get_cfg(target_env)
        target_build = component.get_latest_build_num(target_env)
        if (target_build == source_build_num) and (target_config.latest_build.status == 'SUCCESSFUL'):
            self.log_message(f'Skipping {promotion_msg}...already completed')
            return
        stdout.write(f'{verb} {promotion_msg}...')
        stdout.flush()
        result = getattr(component, method)(*args)
        if result != 'SUCCESSFUL':
            print('failed...exiting')
            sys_exit(1)
        print('completed')

    def run_ansible_playbook(self) -> str:
        """Run an Ansible playbook."""
        playbook_dir = self.project.artifacts_dir / self.ansible_dir
        ansible_args = [f'--extra-vars=@{f}' for f in self.step_info.values_files] if self.step_info.values_files else []
        ansible_kwargs = self.step_info.ansible_args if self.step_info.ansible_args else {}
        if self.step_info.inventory:
            ansible_args += [f'--inventory={playbook_dir / f}' for f in self.step_info.inventory]
        if self.step_info.variables:
            ansible_kwargs['extra_vars'] = ' '.join([f'{k}={v}' for (k, v) in self.step_info.variables.items()])
        if self.step_info.remote:
            get_stored_artifact(self.step_info.remote, self.project.artifacts_dir)
        log = ''.join(ansible(playbook_dir / self.playbook, *ansible_args, **ansible_kwargs))
        if 'Unable to parse' in log:
            raise StepError(StepError.ANSIBLE_ERROR, msg='Unable to parse inventory')
        if 'Could not match supplied host pattern' in log:
            raise StepError(StepError.ANSIBLE_ERROR, msg='Bad host specification')
        return log

    def tag_source(self, tag: str, label: Optional[str] = None) -> None:
        """Tag the source in GitLab.

        Args:
            tag: The label which which to tag the source.
            label (optional, default=None): The annotation to apply to the tag.

        Returns:
            Nothing.
        """
        self.log_message('Removing local tags and adding remote')
        for local_tag in [t.strip() for t in git('tag', list=True)]:
            git('tag', local_tag, delete=True)
        self.gitlab.client.add_remote_ref('cicd_origin', self.gitlab.CI_REMOTE_REF, exists_ok=True)
        self.log_message(f'Tagging the source with {tag}')
        self.gitlab.client.add_label(tag, label, exists_ok=True)
        self.gitlab.client.checkin_files('Automated pipeline tag check-in [skip ci]', remote='cicd_origin', tags=True, all_branches=False)


class CICDAction:  # pylint: disable=too-few-public-methods
    """This is a base class to build CI/CD support scripts using the BatCave automation module Action class."""
    def __init__(self, action_type: str, action_step_class: CICDStep):
        """
        Args:
            action_type: The action type.
            action_step_class: The Class to use for the action.

        Attributes:
            action_step_class: The value of the action_step_class argument.
            action_type: The value of the action_type argument.
            config: The project configuration.
        """
        self.config = ProjectConfig()
        self.action_type = action_type
        self.action_step_class = action_step_class

    def execute(self) -> None:
        """Run the action."""
        CICDStep().log_message(f'Starting {TITLE} version {VERSION} ({BUILDNAME}) [{BUILDDATE}]', True)
        for (category, info) in (yaml_to_dotmap(TOOL_REPORT) if TOOL_REPORT.exists() else tool_reporter()).items():
            CICDStep().log_message(category.replace('_', ' ').title(), True)
            for (name, data) in info.items():
                CICDStep().log_message(f'  {name}: {data}')
        steps = []
        if self.action_type in self.config.use_steps:
            steps = self.config.use_steps[self.action_type]
        elif hasattr(action_def := getattr(self.config, self.action_type), 'steps'):
            steps = action_def.steps
        if not steps:
            return

        is_first_step = True
        for step in [DotMap(s) for s in steps]:
            step.is_first_step = is_first_step
            verb = 'Skipping' if step.ignore else 'Executing'
            CICDStep().log_message(f'{verb} {self.action_type} step: {step.type if (not step.name) else step.name}', True)
            if step.ignore:
                continue
            (executor := cast(Callable, self.action_step_class)()).step_info = step
            executor.execute()
            is_first_step = False


def get_stored_artifact(artifact_name: str, dest_dir: str, /, *, package_bucket: str = PACKAGE_BUCKET) -> None:
    """Retrieve a remote artifact and unpack the archive.

    Args:
        artifact_name: The name of the remote artifact.
        dest_dir: The directory to which to unpack the retrieved archive.
        package_bucket (optional, default=PACKAGE_BUCKET): The JFrog Artifactory bucket from which to retrieve the artifact.

    Returns:
        Nothing.
    """
    tempdir = Path(mkdtemp())
    try:
        remote_storage = RemoteStorage(package_bucket)
        if not remote_storage.exists(artifact_name):
            raise StepError(StepError.REMOTE_FILE_NOT_FOUND, file=f'{package_bucket}/{artifact_name}')
        remote_storage.retrieve(artifact_name, tempdir)
        unpack(tempdir / artifact_name, dest_dir)
    finally:
        rmpath(tempdir)

# cSpell:ignore batcave builddate buildname cicd cloudmgr connectinfo dotmap fileutil platarch syscmd tfplan vardict varprops
# cSpell:ignore checkin dockerhub oncenter constructconnect servermgr qbpy dicttoxml xmltodict quickbuild xmldata
