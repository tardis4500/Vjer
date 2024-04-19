"""This program prints the tool information.

Attributes:
    PRODUCTS (list): This list of products on which to report.
"""

# Import standard modules
from re import compile as re_compile

# Import third-party modules
from batcave.lang import CommandResult
from batcave.sysutil import syscmd, CMDError
from dotmap import DotMap

PRODUCTS = [DotMap(name='Docker', regex=re_compile('Docker version (.+)')),
            DotMap(name='Google Cloud SDK', command='gcloud', regex=re_compile(r'Google Cloud SDK ([\d\.]+) ')),
            DotMap(name='Helm', args=['version'], regex=re_compile(r'Version:"v([\d\.]+)"'))]


def tool_reporter() -> dict:
    """Construct the tool report.

    Returns:
        A dictionary representing the report. There are three members in the dictionary:
            tool_versions: a dictionary of the tools with their versions.
            helm_plugins: a list of the helm plugins.
            helm_repos: a list of the helm repositories.
    """
    tool_info = DotMap(tool_versions={})
    for product in PRODUCTS:
        tool_info.tool_versions[product.name] = get_version(product)

    tool_info.helm_plugins = get_helm_info('plugin')
    tool_info.helm_repos = get_helm_info('repo')
    return tool_info.toDict()


def get_version(product: DotMap) -> str | list:
    """Determine the version for the specified product.

    Args:
        product: The product for which the version should be returned.

    Returns:
        The version of the specified product.
    """
    version_command = product.command if product.command else product.name.lower()
    version_args = product.args if product.args else ['--version']
    version_info: CommandResult = []
    try:
        version_info = syscmd(version_command, *version_args, ignore_stderr=True, append_stderr=True)
    except FileNotFoundError:
        pass
    except CMDError as err:
        if not (('not found' in str(err)) or ('not be found' in str(err)) or ('command could not be loaded' in str(err))):
            raise
    if product.raw:
        return version_info
    return version[1] if (version := product.regex.search(' '.join([line.strip() for line in version_info]))) else 'Not Found'


def get_helm_info(info_type: str) -> dict:
    """Return the requested Helm info.

    Args:
        info_type: The type of helm info to return.

    Returns:
        A dictionary of the requested info.
    """
    helm_info = {}
    try:
        for line in syscmd('helm', info_type, 'list', ignore_stderr=True):
            if line.startswith('NAME'):
                continue
            (name, url) = line.split()[0:2]
            helm_info[name] = url
    except FileNotFoundError:
        helm_info['Helm'] = 'not installed'
    except CMDError as err:
        if 'no repositories to show' not in ''.join(err.vars['err_lines']):
            raise
        helm_info['found'] = 'none'
    return helm_info if helm_info else {'found': 'none'}

# cSpell:ignore batcave syscmd dotmap
