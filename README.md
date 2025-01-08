# xmipp3-installer
Python package that handles the installation of xmipp3

## Testing the code
The automatic tests for this package can be run using `./scripts/run-tests.sh` in bash, or `.\scripts\run-tests.ps1` in PowerShell.
If you intend to run this tests from within VSCode, you will need extension `Test Adapter Converter`, and a local `.vscode` folder with a file named `settings.json` inside with the following content:
```json
{
  "python.testing.pytestArgs": [
    ".",
    "--capture=no"
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true
}
```
