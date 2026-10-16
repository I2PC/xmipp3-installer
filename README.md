# xmipp3-installer
Python package that handles the installation of [xmipp3](https://github.com/I2PC/xmipp3).

## Installation
To install the package, simply run:
```
pip install xmipp3-installer
```

## Usage
This package has a CLI built-in, with help messages that explain how to use it.
To run such help, once the package is installed, run:
```
xmipp3_installer -h
```

## Installing dependencies with Conda
By default, Xmipp is built against the libraries found in your system. Alternatively, the installer can install Xmipp's dependencies into the **currently active** Conda environment before compiling:
```
conda create -n xmipp3 python
conda activate xmipp3
pip install xmipp3-installer
XMIPP3_INSTALL_CONDA_DEPENDENCIES=ON ./xmipp all
```
The environment is selected from the ones Xmipp defines, according to your NVIDIA driver (or without CUDA if `XMIPP_USE_CUDA=OFF` or no driver is found). To skip the detection, for example on a cluster's login node without GPU, set `XMIPP3_CONDA_ENVIRONMENT` to the id of the environment to use (such as `CUDA12`). In this mode, CUDA is taken only from the Conda environment.

Both variables can also be set in `xmipp.conf` (`INSTALL_CONDA_DEPENDENCIES` and `CONDA_ENVIRONMENT`).

Xmipp's repository must provide `conda/environments.json`, listing its environments by preference, with file paths relative to the repository's root. The first one whose `min_driver_version` the driver meets is selected, and the one without it is the fallback:
```json
{
  "environments": [
    {"id": "CUDA12", "file": "conda/xmipp_CUDA12.yml", "min_driver_version": "525.60.13"},
    {"id": "CPU",    "file": "conda/xmipp_CPU.yml"}
  ]
}
```
Environment files must not pin a different `python` than the environment's (the installer runs inside it), and CUDA ones must include `nvcc`.

## Installation telemetry
This installer collects **basic information about your installation environment** (such as library versions, system architecture, and operating system) to improve compatibility, performance, and stability.

If you prefer **not to send this data**, you can disable data collection by simply setting the environment variable `XMIPP3_SEND_INSTALLATION_STATISTICS=OFF` before running the installation command.

For more information, please visit [the documentation](https://i2pc.github.io/docs/Others/Enhancing/index.html#data-collection).

## Testing the code
In order to run the tests for this project, the project needs to be installed in development mode and also the test dependencies need to be installed.

To do that, you need to clone this project, move inside the repository's folder, and run:
```
pip install -e .[test]
```
Once the dependencies have been installed, the automatic tests for this package can be run using `./scripts/run-tests.sh` in bash, or `.\scripts\run-tests.ps1` in PowerShell.
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

## SonarQube status
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)

### Ratings
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)

### Specific metrics
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=bugs)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=coverage)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=I2PC_xmipp3-installer&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=I2PC_xmipp3-installer)
