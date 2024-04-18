"""Module to hold common values and utility functions for CI/CD support scripts.

Attributes:
    PROJECT_CFG_FILE (str): The name of the project config file.
    TOOL_REPORT (Path): The path of the tool report.

    There are several tool runners defined for simplified usage: git, helm.
"""
# Import standard modules
from copy import deepcopy as copy_object
from datetime import datetime
from os import getenv
from pathlib import Path
from random import randint
from shutil import copy, copyfile, copytree
from stat import S_IWUSR
from string import Template
from sys import exit as sys_exit, stderr
from typing import Callable, cast, Optional

# Import third-party modules
from batcave.automation import Action
from batcave.cloudmgr import Cloud, CloudType, gcloud
from batcave.cms import Client, ClientType
from batcave.expander import Expander, file_expander
from batcave.lang import BatCaveError, BatCaveException, PathName, DEFAULT_ENCODING, WIN32, yaml_to_dotmap
from batcave.platarch import Platform
from batcave.sysutil import CMDError, SysCmdRunner, syscmd
from bumpver.config import init as bumpver_config
from dotmap import DotMap
from flit.build import main as flit_builder
from yaml import safe_dump as yaml_dump, safe_load as yaml_load

# Import project modules
from .tool_reporter import tool_reporter

_CONFIG_SECTIONS = ('project', 'test', 'build', 'deploy', 'rollback', 'release')
_PROJECT_DEFAULTS = DotMap(build_artifacts='artifacts',
                           build_num_var='VJER_BUILD_NUM',
                           chart_root='helm-chart',
                           container_registry=DotMap(type='local', name=''),
                           dockerfile='Dockerfile',
                           test_results='test_results',
                           version_service=DotMap(type='vjer'))
_VALID_SCHEMAS = [3]

PROJECT_CFG_FILE = getenv('VJER_CFG', 'vjer.yml')
TOOL_REPORT = Path(__file__).parent.absolute() / 'tool_report.yml'

HELM_CHART_FILE = 'Chart.yaml'
DEFAULT_VERSION_FILES = {'helm': [HELM_CHART_FILE, 'values.yaml']}

VJER_ENV = getenv('VJER_ENV', 'local')
REMOTE_REF = 'vjer_origin'

apt = SysCmdRunner('apt-get', '-y').run
apt_install = SysCmdRunner('apt-get', '-y', 'install', no_install_recommends=True).run
git = SysCmdRunner('git').run
helm = SysCmdRunner('helm', syscmd_args={'ignore_stderr': True}).run
pip_install = SysCmdRunner('pip', 'install', quiet=True, no_cache_dir=True, upgrade=True).run


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
        UNKNOWN_OBJECT: The specified object is of an unknown type.
    """
    UNKNOWN_OBJECT = BatCaveError(1, Template('Unknown $type: $name'))


class Environment:  # pylint: disable=too-few-public-methods
    """Provides an interface to the environment variables."""

    def __getattr__(self, attr: str):
        value = getenv(attr)
        if value is None:
            raise AttributeError(f'Environment variable not found: {attr}')
        return value


class GitClient(Environment):
    """Provides an interface to the Git server environment and API."""

    def __init__(self, project_id: Optional[str] = None, client_root: Optional[PathName] = None, branch: Optional[str] = None):
        """
        Args:
            project_id (optional, default=None): The ID of the Git project.
            client_root (optional, default=None): The root directory of the project.
            branch (optional, default=None): The branch to use for the Git client.

        Attributes:
            CI_REMOTE_REF: The full git reference to the project.
            branch: The value of the branch argument.
            client: The git client for the project.
            project_id: The value of the project_id argument.
        """
        self.project_id = project_id
        self.client = Client(ClientType.git, 'vjer', connect_info=str(client_root), create=False) if (client_root and (Path(client_root) / '.git').exists()) else None
        self.branch = branch if branch else getattr(self, 'CI_COMMIT_BRANCH', '')

    def __enter__(self):
        return self

    def __exit__(self, *_unused_exc_info):
        return False


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
                    return DotMap({k: self._expander.expand(v) for (k, v) in value.items()})
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

    def update(self, values: dict | DotMap, /) -> None:
        """Update the configuration section values.

        Args:
            values: Update the configuration values from the provided dictionary.

        Returns:
            Nothing.
        """
        self._values |= values

    def update_defaults(self, values: dict | DotMap, /) -> None:
        """Updates the configuration section default values.

        Args:
            values: Update the defaults with the provided dictionary.

        Returns:
            Nothing.
        """
        self._defaults |= values


class ProjectConfig():
    """Stores project related configuration items."""

    def __init__(self):
        """
        Attributes:
            _config_file: The config file for the project configuration.
            _sections: A list of the sections in the project configuration.
            schema: The schema version of the project configuration.
        """
        project_root = Path.cwd()
        self._sections = {'project': ConfigSection(**(DotMap(project_root=project_root) | _PROJECT_DEFAULTS)),
                          'test': ConfigSection(),
                          'deploy': ConfigSection(clean=True),
                          'rollback': ConfigSection(clean=True),
                          'release': ConfigSection()}
        self._sections['build'] = ConfigSection(source_dir=self.project.project_root / 'src',
                                                version_files=[],
                                                artifacts={},
                                                build_date=str(datetime.now()),
                                                platform=Platform().bart)
        self._config_file = self.project.project_root / PROJECT_CFG_FILE
        self._load_config()
        self._set_defaults()
        self._set_version()

        for section in _CONFIG_SECTIONS:
            self._sections[section].update_expander(property_holders=list(self._sections.values()))

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

    def _load_config(self) -> None:
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

    def _set_defaults(self) -> None:
        self.project.update_defaults(DotMap(artifacts_dir=self.project.project_root / self.project.build_artifacts,
                                            test_results_dir=self.project.project_root / self.project.test_results))
        if hasattr(self.project, 'artifact_repo'):
            if hasattr(self.project, 'docker_repo'):
                self.project.update_defaults(DotMap(container_registry=DotMap(self.project.docker_repo)))
            if hasattr(self.project, 'helm_repo'):
                self.project.update_defaults(DotMap(chart_repo=DotMap(self.project.helm_repo)))

    def _set_version(self) -> None:
        match self.project.version_service.type:
            case 'bumpver':
                self.project.version = bumpver_config()[1].pep440_version
            case 'environment':
                self.project.version = getenv(self.project.version_service.variable, '').rstrip('.')
            case 'vjer':
                pass
            case _:
                print('Unknown version service:', self.project.version_service.type, file=stderr)
                sys_exit(1)
        build_num = getenv(self.project.build_num_var, '0')
        build_version = f'{self.project.version}-{build_num}'
        self.build.update_defaults(DotMap(build_num=build_num,
                                          build_version=build_version,
                                          build_version_msbuild=f'{self.project.version}.{build_num}',
                                          build_name=f'{self.project.name}_{build_version}'))
        self.release.update_defaults(DotMap(release_tag=f'v{self.project.version}'))
        for (piece, index) in {'major': 0, 'minor': 1, 'patch': 2}.items():
            self.project.update_defaults({f'{piece}': self.project.version.split('.', 2)[index]})

    filename = property(lambda s: s._config_file, doc='A read-only property which returns the configuration file name.')

    def write(self) -> None:
        """Writes out the project configuration.

        Returns:
            Nothing.
        """
        with open(self._config_file, 'w', encoding=DEFAULT_ENCODING) as config_file:
            yaml_dump({'schema': self.schema} | {s: c.values for (s, c) in self._sections.items() if c.values},
                      config_file, indent=2)


class VjerStep(Action):  # pylint: disable=too-many-instance-attributes
    """ Class to represent a single Action step."""

    def __init__(self):
        """
        Attributes:
            build: The project build configuration.
            config: The project configuration.
            docker_client: The Docker client.
            git_client: The Git repository for the project.
            image_name: The Docker image name.
            image_tag: The Docker image tag.
            pre_release_num: The pre_release suffix for the project.
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
        self.git_client = GitClient(client_root=self.project.project_root)
        self.step_info = DotMap()
        self.pre_release_num = self.build.build_num
        # Used by Docker builds
        self.registry_client = None
        self.docker_client = None
        self.image_name = ''
        self.version_tag = ''
        self.image_tag = ''

    def __getattr__(self, attr: str):
        if not hasattr(self.project, attr):
            raise AttributeError(f'No such attribute: {attr}')
        return getattr(self.step_info, attr) if getattr(self.step_info, attr) else getattr(self.project, attr)

    def _docker_init(self, login: bool = True) -> None:
        """Perform Docker initialization.

        Args:
            login (optional, default=True): If True, login to the Docker image registry.
            mode (optional, default='pull'): The mode for which this initialization will be used.

        Returns:
            Nothing.
        """
        self.registry_client = Cloud(CloudType.gcloud if (self.container_registry.type == 'gcp') else CloudType.local, login=login)
        self.docker_client = Cloud(CloudType.local)
        registry_name_path = f'{self.container_registry.name}/' if login else ''
        self.image_name = f'{registry_name_path}{self.step_info.image if self.step_info.image else self.project.name}'
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
    pkg_name = property(lambda s: f'{s.step_info.pkg_name if s.step_info.pkg_name else s.project.name}-{s.project.version}',
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
        if (self.chart_repo.type != 'oci') and self.chart_repo.url and not self.chart_repo.name:
            repo_name = f'vjer-{randint(0, 100)}'
            helm('repo', 'add', repo_name, self.chart_repo.url)
            helm('repo', 'update')
            self.chart_repo.name = repo_name
        return self.chart_repo

    def commit_files(self, message: str, branch: str, *files, file_updater: Optional[Callable] = None) -> None:
        """Checkin files during to the source repository."""
        self.git_client.client.add_remote_ref(remote_ref := REMOTE_REF, self.git_client.CI_REMOTE_REF, exists_ok=True)
        git('fetch', all=True, syscmd_args={'ignore_stderr': True})
        git('remote', 'update', remote_ref, prune=True, syscmd_args={'ignore_stderr': True})
        git('checkout', '-B', branch, '--track', f'{remote_ref}/{branch}', syscmd_args={'ignore_stderr': True})
        git('pull', remote_ref, branch, syscmd_args={'ignore_stderr': True})
        if file_updater:
            file_updater()
        self.git_client.client.add_files(*files)
        self.git_client.client.checkin_files(message, remote=remote_ref, all_branches=False)

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

    def flit_build(self) -> None:
        """Run a Python flit build."""
        flit_builder(Path('pyproject.toml'))
        self.copy_artifact('dist')

    def helm_build(self) -> None:
        """Build a Helm chart."""
        helm('package', self.helm_chart_root)
        self.copy_artifact(self.helm_package.name)

    def tag_images(self, source_tag: str, tags: list[str]) -> None:
        """Tag Docker images.

        Args:
            source_Tag: The tag of the existing image to which to add the new tags.
            tags: The list of tags to add.

        Returns:
            Nothing.
        """
        if (registry := self.container_registry).type not in ('gcp', 'gcp-art'):
            (image := self.registry_client.get_image(source_tag)).pull()
        for tag in tags:
            self.log_message(f'Tagging image: {tag}')
            match registry.type:
                case 'gcp':
                    gcloud('container', 'images', 'add-tag', source_tag, tag, syscmd_args={'ignore_stderr': True})
                case 'gcp-art':
                    gcloud('artifacts', 'docker', 'tags', 'add', source_tag, tag, syscmd_args={'ignore_stderr': True})
                case  _:
                    image.tag(tag)
                    image.push()

    def tag_source(self, tag: str, label: Optional[str] = None) -> None:
        """Tag the source in Git.

        Args:
            tag: The label which which to tag the source.
            label (optional, default=None): The annotation to apply to the tag.

        Returns:
            Nothing.
        """
        self.log_message('Removing local tags and adding remote')
        for local_tag in [t.strip() for t in git('tag', list=True)]:
            git('tag', local_tag, delete=True)
        self.git_client.client.add_remote_ref(REMOTE_REF, self.git_client.CI_REMOTE_REF, exists_ok=True)
        self.log_message(f'Tagging the source with {tag}')
        self.git_client.client.add_label(tag, label, exists_ok=True)
        self.git_client.client.checkin_files('Automated pipeline tag check-in [skip ci]', remote=REMOTE_REF, tags=True, all_branches=False)

    def update_version_files(self, *, reset: bool = False) -> None:  # pylint: disable=too-many-branches
        """Updates the version files for the project.

        Args:
            reset (optional, default=False): If True, reset the files.

        Returns:
            Nothing.
        """
        verb = 'Resetting' if reset else 'Updating'

        if not self.step_info.version_files:
            self.step_info.version_files = []

        match self.step_info.type:
            case 'helm':
                prefix = self.helm_chart_root
            case 'python_module':
                prefix = self.python_module_source
            case _:
                prefix = Path('.')

        if self.step_info.type in DEFAULT_VERSION_FILES:
            self.step_info.version_files += [prefix / v for v in DEFAULT_VERSION_FILES[self.step_info.type] if (prefix / v).exists()]

        if not self.step_info.version_files:
            return

        self.log_message(f'{verb} version files', True)
        for file_name in self.step_info.version_files:
            file_path = Path(file_name)
            msg = f'{verb}: {file_path}'
            file_orig = Path(str(file_path) + '.orig')
            if reset:
                if file_orig.exists():
                    self.log_message(msg)
                    if file_path.exists():
                        file_path.unlink()
                    file_orig.rename(file_path)
            else:
                self.log_message(msg)
                file_path.chmod(file_path.stat().st_mode | S_IWUSR)
                copyfile(file_path, file_orig)
                file_expander(file_orig, file_path, var_props=(self.project, self.build, self.step_info))
                if file_path.name == HELM_CHART_FILE:
                    with open(file_path, encoding=DEFAULT_ENCODING) as yaml_stream:
                        helm_info = yaml_load(yaml_stream)
                    helm_info['version'] = self.project.version
                    if self.step_info.set_app_version:
                        helm_info['appVersion'] = self.project.version
                    with open(file_path, 'w', encoding=DEFAULT_ENCODING) as yaml_stream:
                        yaml_dump(helm_info, yaml_stream)


class VjerAction:  # pylint: disable=too-few-public-methods
    """This is a base class to build CI/CD support scripts using the BatCave automation module Action class."""
    def __init__(self, action_type: str, action_step_class: VjerStep):
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
        for (category, info) in (yaml_to_dotmap(TOOL_REPORT) if TOOL_REPORT.exists() else tool_reporter()).items():
            VjerStep().log_message(category.replace('_', ' ').title(), True)
            for (name, data) in info.items():
                VjerStep().log_message(f'  {name}: {data}')
        if not hasattr(action_def := getattr(self.config, self.action_type), 'steps'):
            return

        is_first_step = True
        for step in [DotMap(s) for s in action_def.steps]:
            step.is_first_step = is_first_step
            VjerStep().log_message(f'Executing {self.action_type} step: {step.type if (not step.name) else step.name}', True)
            (executor := cast(Callable, self.action_step_class)()).step_info = step
            executor.execute()
            is_first_step = False

# cSpell:ignore batcave bumpver cloudmgr dotmap platarch syscmd vjer checkin
