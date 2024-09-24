if ($env:DEBUG -eq 'true') {
  Set-PSDebug -Trace 1
}

$ROOT_DIR = Split-Path $PSScriptRoot -Parent
$LAST_LOCATION = Get-Location
Set-Location $ROOT_DIR

$RCFILE="$ROOT_DIR\conf\.coveragerc"
python -m pytest -v --cache-clear --cov --cov-config=$RCFILE --junitxml=report.xml --cov-report xml --cov-report term

Set-Location $LAST_LOCATION
