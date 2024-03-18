#!/usr/bin/env python3
"""This module creates a Python freeze file for the project.

Attributes:
    PROJECT_ROOT (Path): The root directory of the project.
    FREEZE_FILE_EXT (str): The extension for the frozen requirements file.
    REQUIREMENTS_FILE (Path): The full path of the frozen requirements file.
    FREEZE_FILE_BASE (str): The base name of the frozen requirements file.
    LINUX_MODULES (list): A list of modules that should be limited to the linux platform.
    WINDOWS_MODULES (list): A list of modules that should be limited to the Windows platform.
"""

# Import standard modules
import os
from pathlib import Path
from sys import argv
from tempfile import mkdtemp
from venv import EnvBuilder

# Import BatCave modules
from batcave.fileutil import slurp, spew
from batcave.lang import WIN32
from batcave.sysutil import rmpath, syscmd, SysCmdRunner

from .utils import DEFAULT_ENCODING

PROJECT_ROOT = Path.cwd()
FREEZE_FILE_EXT = '.txt'
REQUIREMENTS_FILE = (PROJECT_ROOT / 'requirements').with_suffix(FREEZE_FILE_EXT)
FREEZE_FILE_BASE = 'requirements-frozen'
LINUX_MODULES: list = []
WINDOWS_MODULES = ['WMI']

pip = SysCmdRunner('pip', show_cmd=False, show_stdout=False, syscmd_args={'ignore_stderr': True}).run


def freeze() -> None:
    """Create the requirement-freeze.txt file leaving out the development tools and adding platform specifiers."""
    freeze_file = (PROJECT_ROOT / (FREEZE_FILE_BASE + (f'-{argv[1]}' if (len(argv) > 1) else ''))).with_suffix(FREEZE_FILE_EXT)
    print('Creating virtual environment in:', venv_dir := Path(mkdtemp()))
    EnvBuilder(with_pip=True).create(venv_dir)
    python = ((venv_bin := venv_dir / ('Scripts' if WIN32 else 'bin')) / 'python').with_suffix('.exe' if WIN32 else '')
    os.environ['PATH'] = os.path.pathsep.join((str(venv_bin), os.environ['PATH']))
    print('Upgrading pip')
    syscmd(str(python), '-m', 'pip', 'install', '-qqq', '--upgrade', 'pip')
    print('Updating pip install tools')
    pip('install', '-qqq', 'setuptools', 'wheel', upgrade=True)
    print('Installing modules from', REQUIREMENTS_FILE)
    pip('install', '-qqq', upgrade=True, requirement=REQUIREMENTS_FILE)
    print('Creating frozen requirements file:', freeze_file)
    spew(freeze_file, pip('freeze', requirement=REQUIREMENTS_FILE))
    freeze_file_contents = [line.strip() for line in slurp(freeze_file)]
    with open(freeze_file, 'w', encoding=DEFAULT_ENCODING) as freeze_file_stream:
        for line in freeze_file_contents:
            module = line.split('==')[0]
            if ('win32' in module) or (module in WINDOWS_MODULES):
                line += "; sys_platform == 'win32'"
            if ('ansible' in module) or (module in LINUX_MODULES):
                line += "; sys_platform != 'win32'"
            print(line, file=freeze_file_stream)
    rmpath(venv_dir)

# cSpell:ignore batcave fileutil syscmd
