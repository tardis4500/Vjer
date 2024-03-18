#!/usr/bin/env python
"""This program provides build job actions.

Attributes:
    P2_ENVIRONMENTS (DotMap): The list of Platform2 environments with information used by the build database.
    P2_SERVICES (list): The list of Platform2 backend services with information about how they are deployed to disk.
"""

# Import standard modules
from copy import copy as object_copy
from os import getenv
from pathlib import Path
from shutil import copy, copyfile, copytree
from stat import S_IWUSR
from string import Template
import sys
from sys import exit as sys_exit
from tempfile import mkdtemp
from typing import cast, Optional

# Import third-party modules
from batcave.configmgr import ConfigCollection
from batcave.expander import file_expander, Expander
from batcave.fileutil import pack, spew
from batcave.lang import str_to_pythonval, WIN32, dotmap_to_yaml, yaml_to_dotmap
from batcave.sysutil import popd, rmpath, syscmd
from docker.errors import BuildError as DockerBuildError
from dotmap import DotMap
from setuptools.sandbox import run_setup
from yaml import dump as yaml_dump, full_load as yaml_load

# Import project modules
from utils import CICDAction, CICDStep, DEFAULT_ENCODING, GitLab, helm, ProjectConfig

if WIN32:
    from pyodbc import connect  # pylint: disable=import-error,no-name-in-module

_DOTNET_BUILD_CONFIG = 'Release'
_DEFAULT_DOTNET_VERSION = '6.0'
_HELM_CHART_FILE = 'Chart.yaml'

DEFAULT_ENVIRONMENTS = ('staging', 'staging2', 'production', 'production2')
DEFAULT_ACTIONS = ('deploy', 'rollback')
PIPELINE_SUPPORT_DIR = Path('deployment_pipeline')
PIPELINE_FILE = 'pipeline.yml'
COMPONENT_DEFINITION_FILE = Path('component-definitions.yml')
RELEASE_DEFINITION_FILE = Path('release-definition.yml')
PIPELINE_ACTION_TEMPLATE = Template(f'''
$action $environment $component:
  extends: .$action-$environment-parallel
  variables:
    PRODUCT: $component
    PROJECT_CFG: {PIPELINE_SUPPORT_DIR}/$component.yml
''')


P2_ENVIRONMENTS = DotMap(feature=DotMap(environment_id=201, branch_id=67, _dynamic=False),
                         develop=DotMap(environment_id=202, branch_id=64, _dynamic=False),
                         rc=DotMap(environment_id=202, branch_id=65, _dynamic=False), _dynamic=False)
P2_SERVICES = [DotMap(directory='Cst.Services.Agents', move=('Cst.Services.Agent.AlertLog', 'Cst.Services.Agent.Autosearch', 'Cst.Services.Agent.Directory',
                                                             'Cst.Services.Agent.DirectoryLog', 'Cst.Services.Agent.Document', 'Cst.Services.Agent.DPULog',
                                                             'Cst.Services.Agent.File', 'Cst.Services.Agent.Mail', 'Cst.Services.Agent.Project',
                                                             'Cst.Services.Agent.Query', 'Cst.Services.Agent.VO')),
               DotMap(directory='Convert.Server', copy=('Cst.Services.Agent.Autosearch', 'Cst.Services.Agent.Document', 'Cst.Services.Agent.File',
                                                        'Cst.Services.Agent.Query', 'Cst.Services.Agent.VO')),
               DotMap(directory='ITB.Server', copy=('Cst.Services.Agent.Directory', 'Cst.Services.Agent.DirectoryLog', 'Cst.Services.Agent.Mail',
                                                    'Cst.Services.Agent.Project', 'Cst.Services.Agent.Query', 'Cst.Services.Agent.VO')),
               DotMap(directory='OrphanedFiles.Server', move=['Cst.Tasks.OrphanedFiles']),
               DotMap(directory='Utility.Server', move=('Cst.Services.Agent.SkinnyDocSearch', 'Cst.Services.Agent.Zip', 'Cst.TimeoutManager'),
                      copy=('Cst.Services.Agent.AlertLog', 'Cst.Services.Agent.Autosearch', 'Cst.Services.Agent.Directory', 'Cst.Services.Agent.DirectoryLog',
                            'Cst.Services.Agent.Document', 'Cst.Services.Agent.DPULog', 'Cst.Services.Agent.File', 'Cst.Services.Agent.Mail',
                            'Cst.Services.Agent.Project', 'Cst.Services.Agent.Query', 'Cst.Services.Agent.VO'))]


class ComponentConfig:
    """Class to hold the component configuration information."""
    def __init__(self, name: str, config: ProjectConfig):
        self.name = name
        self._config = config
        self._steps = DotMap(deploy=DotMap(steps=[]), rollback=DotMap(steps=[]))
        if self.name == 'kubetastic':
            self._steps.deploy.steps.append(DotMap(type='qb', components=[]))
            self._steps.rollback.steps.append(DotMap(type='qb', components=[]))

    @property
    def dotmap(self) -> DotMap:
        """Property to return the DotMap representation of the config."""
        return DotMap(schema=1,
                      project=DotMap(product=self._config.project.product, version=self._config.project.version),
                      deploy=DotMap(steps=[]),
                      rollback=DotMap(steps=[])) | self._steps

    def _add_step(self, step_type: str, step: DotMap, release_info: DotMap) -> None:
        expander = Expander(var_props=release_info)
        if self.name == 'kubetastic':
            self._steps[step_type].steps[0].components.append(expander.expand(step))
            return
        match step.type:
            case 'helm':
                if ('helm_args' in step) and ('version' in step.helm_args):
                    step.helm_args.version = str(expander.expand(step.helm_args.version))
            case 'ansible':
                step.remote = str(expander.expand(step.remote))
                if 'variables' in step:
                    expanded_vars = {}
                    for (var, val) in step.variables.items():
                        expanded_vars[var] = object_copy(release_info[var]) if isinstance(release_info[var], list) else expander.expand(val)
                    step.variables = expanded_vars
            case 'qb':
                step = expander.expand(step)
        self._steps[step_type].steps.append(step)

    def add_deploy_step(self, step: DotMap, release_info: DotMap) -> None:
        """Add a deployment step."""
        self._add_step('deploy', step, release_info)

    def add_rollback_step(self, step: DotMap, release_info: DotMap) -> None:
        """Add a rollback step."""
        self._add_step('rollback', step, release_info)


class BuildStep(CICDStep):
    """This class provides build support.

        Build processing flow:
          pre:
              remove an old artifact directory
              create the artifact directory
              update the version files
          execute:
              run the inheriting build() method for the project type
          post:
              revert the version files

    Attributes:
        DEFAULT_VERSION_FILES: The default version files for the build types.
    """
    DEFAULT_VERSION_FILES = {'helm': [_HELM_CHART_FILE, 'values.yaml'],
                             'python_module': ['__init__.py']}

    def __init__(self, **args):
        """
        Args:
            **args: Arguments to pass through to the parent class

        Attributes:
            all_files_glob: The default lst of files.
        """
        super().__init__(**args)
        self.all_files_glob = DotMap(name='*')

    def _execute(self) -> None:
        """This method is called by the Action super class when this class's execute method is called.
            Performs post-build steps as defined in the project config."""
        super()._execute()
        if self.step_info.archive_artifacts:
            self.archive_artifacts()
        if self.step_info.jfrog_upload:
            self.jfrog_upload()
        if self.step_info.p2_dvfile_upload:
            self._p2_dvfile_upload()

    def _p2_dvfile_upload(self) -> None:
        """Upload a file the the legacy dvfile file server."""
        if self.step_info.is_p2:
            for server in P2_SERVICES:
                (server_path := self.project.artifacts_dir / server.directory).mkdir()
                for action in ('move', 'copy'):
                    for agent in server[action]:
                        source = self.project.artifacts_dir
                        if action == 'copy':
                            source /= 'Cst.Services.Agents'
                            verb = 'Copying'
                        else:
                            verb = 'Moving'
                        source /= agent
                        target = server_path / agent
                        self.log_message(f'{verb} {source} to {target}')
                        if action == 'move':
                            source.rename(target)
                        else:
                            self.copy_artifact(source, target)
        if self.step_info.net_use:
            syscmd('net', 'use', self.step_info.net_use.share, f'/user:{self.step_info.net_use.user}', self.step_info.net_use.password)
        for source_file in self.project.artifacts_dir.iterdir():
            self.copy_artifact(source_file, Path(self.step_info.target) / source_file.name)

    python_module_source = property(lambda s: Path(s.step_info.module_name) if s.step_info.module_name else Path.cwd(),
                                    doc='A read-only property which returns the root of the module source.')

    def pre(self) -> None:
        """This method is run at the start of the build."""
        super().pre()
        if self.step_info.is_first_step:
            self.log_message('Preparing artifact directory', True)
            if Path(self.project.artifacts_dir).exists():
                self.log_message(f'Removing stale artifact directory: {self.project.artifacts_dir}')
                rmpath(self.project.artifacts_dir)
            if not Path(self.project.artifacts_dir).exists():
                self.log_message(f'Creating clean artifact directory: {self.project.artifacts_dir}')
                Path(self.project.artifacts_dir).mkdir(parents=True)
        self.update_version_files()

    def post(self) -> None:
        """This method is run at the end of the build."""
        super().post()
        self.log_message('Build Completed Successfully', True)
        if self.step_info.jfrog_publish and not str_to_pythonval(getenv('NO_REMOTE_ARTIFACT_STORAGE', '')):
            for artifact in self.step_info.jfrog_publish.artifacts:
                self.publish_package(self.project.artifacts_dir / artifact, package_bucket=self.step_info.jfrog_publish.bucket)

    def always_post(self) -> None:
        """This method is always run at the end of the build."""
        super().always_post()
        self.update_version_files(reset=True)

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

        if self.step_info.type in self.DEFAULT_VERSION_FILES:
            self.step_info.version_files += [prefix / v for v in self.DEFAULT_VERSION_FILES[self.step_info.type] if (prefix / v).exists()]

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
                if file_path.name == _HELM_CHART_FILE:
                    with open(file_path, encoding=DEFAULT_ENCODING) as yaml_stream:
                        helm_info = yaml_load(yaml_stream)
                    helm_info['version'] = self.project.version
                    if self.step_info.set_app_version:
                        helm_info['appVersion'] = self.project.version
                    with open(file_path, 'w', encoding=DEFAULT_ENCODING) as yaml_stream:
                        yaml_dump(helm_info, yaml_stream)

    def create_archive(self, name: str, what: list, /, *, location: Optional[str] = None, arc_type: Optional[str] = None, use_tmpdir: bool = False) -> None:  # pylint: disable=too-many-arguments
        """Helper function to create an archive. When complete, the archive is copied to the project build artifact directory.

        Args:
            name: The archive file name.
            what: The files to include in the archive.
            location (optional, default=None): The location of the files to archive. If None, the current directory is used.
            arc_type (optional, default=None): The type of the archive. If None, is inferred from the file extension.
            use_tmpdir (optional, default=False): If True, create the archive in a temporary directory.

        Returns:
            Nothing.
        """
        package_dir = Path(mkdtemp()) if use_tmpdir else self.project.artifacts_dir
        package = package_dir / name
        try:
            self.log_message(f'Creating "{package}" archive from: {",".join(what)}', True)
            pack(package, what, item_location=location, archive_type=str(arc_type), ignore_empty=False)
            copyfile(package, self.project.artifacts_dir / name)
        finally:
            if use_tmpdir:
                rmpath(package_dir)

    def build_ansible(self) -> None:
        """Run an Ansible build."""
        if not self.step_info.artifacts:
            self.step_info.artifacts = [DotMap(source_dir=self.ansible_dir,
                                               files=[self.all_files_glob],
                                               excludes=['terraform_output.json'],
                                               source_path=self.project.project_root,
                                               target_dir=self.ansible_dir)]
        self.build_filecopy()

    def build_configurations(self) -> None:
        """Build method to build a configuration collection."""
        for config in ConfigCollection(self.project.product):
            (cfg_build_dir := self.project.artifacts_dir / config.name).mkdir(parents=True)
            self.log_message(f'Processing configuration "{config.name}" to "{cfg_build_dir}"', True)
            expander = Expander(var_props=config)
            for source_path in self.step_info.source_dir.iterdir():
                self.log_message(f'Expanding: {source_path}')
                target = cfg_build_dir / source_path.name
                if source_path.is_dir():
                    expander.expand_directory(source_path, target)
                else:
                    expander.expand_file(source_path, target)
            for ver_file in self.step_info.version_files:
                self.copy_artifact(ver_file, config.name)
        popd()

    def build_deployer(self) -> None:
        """The main entry point."""
        pipeline = ['variables: {}']
        component_definitions = yaml_to_dotmap(COMPONENT_DEFINITION_FILE)
        component_configs = {}
        for (component, release_info) in yaml_to_dotmap(RELEASE_DEFINITION_FILE).items():
            self.log_message(f'Processing Component: {component}', guard=True)
            if component not in component_definitions:
                self.log_message(f'Unknown component: {component}', leader='ERROR')
                sys_exit(1)
            if release_info.version == 'NA':
                self.log_message('...not included in this release')
                continue
            component_definition = component_definitions[component]
            pipeline_component_name = component_definition.parent if component_definition.parent else component
            if pipeline_component_name not in component_configs:
                for environment in (component_definition.environments if component_definition.environments else DEFAULT_ENVIRONMENTS):
                    for action in (component_definition.actions if component_definition.actions else DEFAULT_ACTIONS):
                        pipeline.append(PIPELINE_ACTION_TEMPLATE.substitute(action=action, environment=environment, component=pipeline_component_name))
                component_configs[pipeline_component_name] = ComponentConfig(pipeline_component_name, self.config)

            for step in component_definition.deploy:
                component_configs[pipeline_component_name].add_deploy_step(step, release_info)
            for step in component_definition.rollback:
                component_configs[pipeline_component_name].add_rollback_step(step, release_info)

        spew(pipeline_path := PIPELINE_SUPPORT_DIR / PIPELINE_FILE, pipeline)
        pipeline_files = [pipeline_path]
        for (component, config) in component_configs.items():
            dotmap_to_yaml(config.dotmap, component_file := PIPELINE_SUPPORT_DIR / f'{component}.yml')
            pipeline_files.append(component_file)
        self.commit_files('Automated deployment pipeline update [skip ci]', self.gitlab.CI_COMMIT_REF_NAME, *pipeline_files)

    def build_docker(self) -> None:
        """Run a Docker build."""
        self._docker_init(not str_to_pythonval(getenv('NO_REMOTE_DOCKER_REGISTRY', '')))
        self.log_message(f'Building docker image: {self.image_tag}', True)
        build_args = {'VERSION': self.project.version,
                      'BUILD_VERSION': self.build.build_version} | self.step_info.build_args
        try:
            log = self.docker_client.client.images.build(rm=True, pull=True, tag=self.image_tag,  # pylint: disable=no-member
                                                         dockerfile=(self.dockerfile),
                                                         buildargs=build_args.toDict(),
                                                         path=str(self.project.project_root))[1]
            error = None
        except DockerBuildError as err:
            error = err
            log = err.build_log
        for line in log:
            if ('stream' in line) and (line['stream'] != '\n'):
                self.log_message(line['stream'].strip())
        if error:
            raise error
        if self.registry_client:
            self.log_message('Pushing image to registry', True)
            self.registry_client.get_image(self.image_tag).push()

    def build_exec(self) -> None:
        """Build method for syscmd runner."""
        syscmd(self.step_info.command, *self.step_info.args, **({'show_cmd': True, 'show_stdout': True, 'use_shell': True} | self.step_info.executor_args))

    def build_filecopy(self) -> None:
        """Build method to copy files."""
        for artifact in self.step_info.artifacts:
            target_path = self.project.artifacts_dir
            if artifact.target_dir:
                target_path /= artifact.target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            for source_file_spec in artifact.files:
                source_path = Path(artifact.source_dir if artifact.source_dir else self.build.source_dir)
                for source_file in source_path.glob(source_file_spec.name):
                    if source_file.name not in artifact.excludes:
                        target_file_name = source_file_spec.rename if source_file_spec.rename else source_file.name
                        target_file = f'{source_file.stem}-{self.project.version}{source_file.suffix}' if source_file_spec.versioned else target_file_name
                        self.copy_artifact(source_file, target_path / target_file)
        for ver_file in self.step_info.version_files:
            self.copy_artifact(ver_file)

    def build_helm(self) -> None:
        """Build method for Helm charts."""
        helm('dependency', 'build', self.helm_chart_root)
        helm('package', self.helm_chart_root)
        self.copy_artifact(self.helm_package.name)

    def build_info_db(self) -> None:
        """Publish the build record in the build info database."""
        cursor = connect(';'.join([f'{var}={val}' for (var, val) in self.step_info.connection_string.items()])).cursor()
        cursor.execute('SELECT GETDATE()')
        date = cursor.fetchone()[0]
        if self.step_info.is_p2:
            branch_name = self.project.p2_branch
            branch_id = P2_ENVIRONMENTS[branch_name].branch_id
            environment_id = P2_ENVIRONMENTS[branch_name].environment_id
            application_id = 1
        else:
            branch_name = None
            branch_id = 0
            environment_id = self.step_info.environment_id
            application_id = None
        cursor.execute('{CALL dbo.InsertBuildInfo (?,?,?,?,?,?,?)}',
                       (environment_id, self.build.build_version_msbuild, self.step_info.build_label, date, branch_id, branch_name, application_id))
        cursor.commit()
        if cursor.messages:
            self.log_message(cursor.messages)

    def build_k8s(self) -> None:
        """Run a Kubernetes build."""
        if not self.step_info.artifacts:
            self.step_info.artifacts = [DotMap(source_dir='kubernetes', files=[self.all_files_glob], target_dir='kubernetes')]
        self.build_filecopy()

    def build_msbuild(self) -> None:  # pylint: disable=too-many-branches
        """Run an MSBuild project build."""
        solution = self.buildfile + '.sln'
        target = f'/target:{self.build_project}' if self.build_project else ''
        build_output = (self.automation_root / 'PrecompiledWeb') \
            if (self.ptype == self.VS_PROJECT_TYPES.website) else (self.step_info.build_staging if self.step_info.build_staging else self.ci_artifacts)

        if self.nuget_list is not None:
            nuget_list = [solution] + [Path(p, 'packages.config') for p in self.nuget_list]
            if self.ptype == self.VS_PROJECT_TYPES.website:
                nuget_list.append(Path(self.web_project, 'packages.config'))
            self.nuget_restore(nuget_list)

        build_options = f'/property:Configuration={self.vs_cfg};Platform={self.vs_platform}'
        if self.redirect_output:
            build_options += f';OutDir={build_output}'
        self.msbuild('Building solution', solution, target, build_options)

        if self.ptype == self.VS_PROJECT_TYPES.db:
            self.log_message('Collecting deployment files', True)
            for subdir in self.project_root.iterdir():
                if not subdir.is_dir():
                    continue
                deployment_src = subdir / 'Publishers'
                deployment_art = self.ci_artifacts / subdir.name
                if deployment_src.exists():
                    self.log_message(f'Copying deployment files for {subdir.name}')
                    copytree(deployment_src, deployment_art)

        if self.step_info.build_staging:
            self.log_message('Copying artifacts', True)
            match self.ptype:
                case self.VS_PROJECT_TYPES.webapp:
                    self.step_info.build_staging = self.build_staging / '_PublishedWebsites' / self.website
                case self.VS_PROJECT_TYPES.website:
                    self.step_info.build_staging = self.build_staging / self.website

            for item in self.build_staging.iterdir():
                if item.suffix == '.orig':
                    continue
                self.log_message(f'Copying: {item}')
                if item.is_dir():
                    copytree(item, self.ci_artifacts / item.name, symlinks=True, ignore_dangling_symlinks=True)
                else:
                    copy(item, self.ci_artifacts)

    def build_python_module(self) -> None:
        """Build method for standard Python setuptools module."""
        sys_path_keeper = sys.path
        sys.path.insert(0, str(self.project.project_root))
        run_setup('setup.py', ['sdist', f'--dist-dir={self.project.artifacts_dir}', 'bdist_wheel', f'--dist-dir={self.project.artifacts_dir}'])
        sys.path = sys_path_keeper

    def build_umbrella(self) -> None:
        """Perform an umbrella build."""
        for component_dict in self.project.components:
            component = DotMap(component_dict)
            self.log_message(f'Processing: {component.name}')
            with GitLab(project_id=component.id, branch=component.branch) as gitlab_project:
                component_cfg = gitlab_project.project_cfg
                image_tag = component.image_tag if component.image_tag else f'{component_cfg.project.version}-{gitlab_project.latest_build_num}'
                updated_steps = []
                for step in component_cfg.deploy.steps:
                    if step.type == 'helm':
                        step.helm_args.version = image_tag
                        step.remote = True
                    updated_steps.append(step)
                component_cfg.deploy.steps = updated_steps
                dotmap_to_yaml(component_cfg, Path(self.project.artifacts_dir, f'{component.name}.yml'))


def main() -> None:
    """This is the main entry point."""
    CICDAction('build', cast(CICDStep, BuildStep)).execute()


if __name__ == '__main__':
    main()

# cSpell:ignore batcave bdist buildargs cicd configmgr dotmap filecopy fileutil nologo pythonval sdist tfplan varprops itemloc
# cSpell:ignore arctype buildfile syscmd autosearch dvfile getdate
