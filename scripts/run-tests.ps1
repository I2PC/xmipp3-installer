param (
  [string]$TestType = "all"
)

if ($env:DEBUG -eq 'true') {
  $DebugPreference = "Continue"
}

$CURRENT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ROOT_DIR = Join-Path $CURRENT_DIR ".."

$RCFOLDER = Join-Path $CURRENT_DIR "../conf/coverage"
$RCFILE_UNITARY = Join-Path $RCFOLDER ".unitary-coveragerc"
$RCFILE_INTEGRATION = Join-Path $RCFOLDER ".integration-coveragerc"
$RCFILE_E2E = Join-Path $RCFOLDER ".e2e-coveragerc"

$CONFIGFOLDER = Join-Path $CURRENT_DIR "../conf/pytest"
$CONFIGFILE_UNITARY = Join-Path $CONFIGFOLDER "unitary.ini"
$CONFIGFILE_INTEGRATION = Join-Path $CONFIGFOLDER "integration.ini"
$CONFIGFILE_E2E = Join-Path $CONFIGFOLDER "e2e.ini"

function Run-Tests {
  param (
    [string]$TestType,
    [string]$RcFile,
    [string]$ConfFile
  )

  Write-Host "Running $TestType tests..."
  $pytestCommand = "python -m pytest -v --cache-clear --cov --cov-config=$RcFile -c=$ConfFile --rootdir=$ROOT_DIR --junitxml=report.xml --cov-report xml --cov-report term"
  Invoke-Expression $pytestCommand
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

Push-Location $ROOT_DIR

  switch ($TestType) {
    "unitary" {
      Run-Tests "unitary" $RCFILE_UNITARY $CONFIGFILE_UNITARY
    }
    "integration" {
      Run-Tests "integration" $RCFILE_INTEGRATION $CONFIGFILE_INTEGRATION
    }
    "e2e" {
      Run-Tests "e2e" $RCFILE_E2E $CONFIGFILE_E2E
    }
    "all" {
      Run-Tests "unitary" $RCFILE_UNITARY $CONFIGFILE_UNITARY
      Run-Tests "integration" $RCFILE_INTEGRATION $CONFIGFILE_INTEGRATION
      Run-Tests "e2e" $RCFILE_E2E $CONFIGFILE_E2E
    }
    default {
      Write-Host "Invalid test type: $TestType"
      Write-Host "Valid types:`n`tall (default)`n`tunitary`n`tintegration`n`te2e"
      exit 1
    }
  }

Pop-Location
