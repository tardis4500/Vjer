#!/usr/bin/env bash
set -eu

if [[ -z ${1:-''} ]]; then
    echo $0 action
    exit 1
fi

PRODUCT=vjer
export FLIT_ROOT_INSTALL=1

unix_os=$(uname)
case $unix_os in
Darwin)
    sw_vers
    ;;
Linux)
    cat /etc/os-release
    ;;
*)
    echo "Unsupported UNIX OS: $unix_os"
    exit 1
    ;;
esac
python --version

function pip-install {
    pip install --upgrade --upgrade-strategy eager $*
}

function install-pip-tools {
    pip-install pip
    pip-install setuptools wheel
}

install-pip-tools
pip-install virtualenv
if [[ ! -e $VIRTUAL_ENV ]]; then virtualenv $VIRTUAL_ENV; fi
source $VIRTUAL_ENV/bin/activate
install-pip-tools
pip-install flit
flit install -s --deps all
if [[ $1 == 'pre_release' || $1 == 'release' ]]; then
    git config user.name "$GIT_AUTHOR_NAME"
    git config user.email "$GIT_AUTHOR_EMAIL"
    git pull
fi
vjer $1

# release)
#     bumpver update --tag final --tag-commit
#     flit build
#     eval $(bumpver show --env)
#     gh release create $CURRENT_VERSION --title="Release $CURRENT_VERSION" --latest --generate-notes
#     bumpver update --patch --tag rc --tag-num
#     ;;
# esac

# cSpell:ignore vjer bumpver virtualenv
