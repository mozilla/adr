#!/usr/bin/env bash

set -ve

pushd /setup

apt-get update
apt-get install -y \
    less \
    python-pip

pip2 install --upgrade mercurial
pip3 install --require-hashes -r requirements.txt

popd
