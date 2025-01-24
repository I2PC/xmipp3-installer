#!/bin/bash

[[ "${DEBUG}" == 'true' ]] && set -o xtrace

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}")" && pwd )"
ROOT_DIR="$CURRENT_DIR/.."

RCFOLDER=$CURRENT_DIR/../conf/coverage
RCFILE_UNITARY=$RCFOLDER/.unitary-coveragerc
RCFILE_INTEGRATION=$RCFOLDER/.integration-coveragerc
RCFILE_E2E=$RCFOLDER/.e2e-coveragerc

CONFIGFOLDER=$CURRENT_DIR/../conf/pytest
CONFIGFILE_UNITARY=$CONFIGFOLDER/unitary.ini
CONFIGFILE_INTEGRATION=$CONFIGFOLDER/integration.ini
CONFIGFILE_E2E=$CONFIGFOLDER/e2e.ini

run_tests() {
    local test_type=$1
    local rcfile=$2
    local conffile=$3

    echo "Running ${test_type} tests..."
    python -m pytest -v --cache-clear --cov --cov-config=$rcfile -c=$conffile --rootdir="${ROOT_DIR}" --junitxml=report.xml --cov-report term
    PYTEST_EXIT_CODE=$?
    if [ $PYTEST_EXIT_CODE -ne 0 ]; then
        exit $PYTEST_EXIT_CODE
    fi
}

pushd "${ROOT_DIR}" > /dev/null

    TEST_TYPE=${1:-all}

    case $TEST_TYPE in
        unitary)
            run_tests "unitary" $RCFILE_UNITARY $CONFIGFILE_UNITARY
            ;;
        integration)
            run_tests "integration" $RCFILE_INTEGRATION $CONFIGFILE_INTEGRATION
            ;;
        e2e)
            run_tests "e2e" $RCFILE_E2E $CONFIGFILE_E2E
            ;;
        all)
            run_tests "unitary" $RCFILE_UNITARY $CONFIGFILE_UNITARY
            run_tests "integration" $RCFILE_INTEGRATION $CONFIGFILE_INTEGRATION
            run_tests "e2e" $RCFILE_E2E $CONFIGFILE_E2E
            python -m coverage combine $RCFOLDER
            python -m coverage xml
            ;;
        *)
            echo "Invalid test type: $TEST_TYPE"
            echo -e "Valid types:\n\tall (default)\n\tunitary\n\tintegration\n\te2e"
            exit 1
            ;;
    esac


popd > /dev/null
