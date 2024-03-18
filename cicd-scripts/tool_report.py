"""This program prints the tool information.

Attributes:
    PRODUCTS (list): This list of products on which to report.
"""

# Import standard modules
from re import compile as re_compile
from sys import stdout

# Import third-party modules
from batcave.commander import Argument, Commander
from batcave.lang import CommandResult, DEFAULT_ENCODING
from batcave.sysutil import syscmd, CMDError
from dotmap import DotMap
from yaml import safe_dump

PRODUCTS = [DotMap(name='Ansible', command='pip', args=['list'], regex=re_compile(r'ansible \s+ ([\d\.]+)')),
            DotMap(name='Docker', regex=re_compile('Docker version (.+)')),
            DotMap(name='.NET SDKs', command='dotnet', args=['sdk', 'check'], raw=True),
            DotMap(name='Google Cloud SDK', command='gcloud', regex=re_compile(r'Google Cloud SDK ([\d\.]+) ')),
            DotMap(name='Helm', args=['version'], regex=re_compile(r'Version:"v([\d\.]+)"')),
            DotMap(name='Java', args=['-version'], regex=re_compile(r'openjdk version "([_\d\.]+)"')),
            DotMap(name='kubectl', args=['version', '--short', '--client'], regex=re_compile(r'Client Version: v([\d\.]+)')),
            DotMap(name='msbuild', regex=re_compile('for .NET Framework (.+)')),
            DotMap(name='sencha', args=['help'], regex=re_compile(r'Sencha Cmd v([\d\.]+)'))]


def main() -> None:
    """Main entry point."""
    args = Commander('BaRT Tool Reporter', [Argument('-o', '--output')]).parse_args()
    safe_dump(tool_reporter(), open(args.output, 'w', encoding=DEFAULT_ENCODING) if args.output else stdout)


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

    in_sdk_list = False
    dotnet_sdks = []
    for line in tool_info.tool_versions['.NET SDKs']:
        if not line.strip():
            break
        if line.startswith('.NET SDKs:'):
            in_sdk_list = True
            continue
        if (not in_sdk_list) or line.startswith('Version') or line.startswith('-'):
            continue
        dotnet_sdks.append(line.split()[0:2][0])
    tool_info.tool_versions['.NET SDKs'] = dotnet_sdks

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
        if 'no repositories to show' not in ''.join(err.vars['errlines']):
            raise
        helm_info['found'] = 'none'
    return helm_info if helm_info else {'found': 'none'}


if __name__ == '__main__':
    main()

# cSpell:ignore batcave dotmap syscmd errlines sencha
