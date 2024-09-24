#!/bin/bash

[[ "${DEBUG}" == 'true' ]] && set -o xtrace

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")" && pwd )"

RCFILE=$CURRENT_DIR/../conf/.coveragerc

pushd "${CURRENT_DIR}"/.. > /dev/null

    python -m pytest -v --cache-clear --cov --cov-config=$RCFILE --junitxml=report.xml --cov-report xml --cov-report term
    PYTEST_EXIT_CODE=$?
    if [ $PYTEST_EXIT_CODE -ne 0 ]; then
        exit $PYTEST_EXIT_CODE
    fi

popd > /dev/null
