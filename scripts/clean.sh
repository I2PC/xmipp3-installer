#!/bin/bash

[[ "${DEBUG}" == 'true' ]] && set -o xtrace

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")" && pwd )"

find $CURRENT_DIR/../ | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
