#!/usr/bin/env bash
set -eu

if [[ -z ${1:-''} ]]; then
    echo $0 action
    exit 1
fi

PRODUCT=vjer
export FLIT_ROOT_INSTALL=1

if [[ $1 == install-test ]]; then
    pip install $ARTIFACTS_DIR/*.tar.gz
    cd tests
    for test in test build release; do
        vjer $test
    done
    exit
fi

pip-install virtualenv
if [[ ! -e $VIRTUAL_ENV ]]; then virtualenv $VIRTUAL_ENV; fi
source $VIRTUAL_ENV/bin/activate
flit install -s --deps all
if [[ $1 == 'pre_release' || $1 == 'release' ]]; then
    git config user.name "$GIT_AUTHOR_NAME"
    git config user.email "$GIT_AUTHOR_EMAIL"
    git pull
fi
vjer $1

# cSpell:ignore vjer virtualenv
