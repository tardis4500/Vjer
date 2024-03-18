$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$PythonVersion = "310"
$PythonHome = "C:\Python$PythonVersion"
$PythonScripts = "$PythonHome\Scripts"
$VirtualEnvironment = "${env:CI_PROJECT_NAME}-${env:CI_COMMIT_BRANCH}-${env:CI_PIPELINE_IID}"

if ($env:CICD_IMAGE_NAME) {
    Write-Host "Using CI/CD support script image ${env:CICD_IMAGE_REPO}${env:CICD_IMAGE_NAME}:${env:CICD_IMAGE_TAG}"
} else {
    try {
        python --version
    } catch {
        choco install python310 --yes --limitoutput --no-progress
        $env:PATH += ";$PythonHome;$PythonScripts"
    }
}

Invoke-Command -ScriptBlock { Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsHardwareAbstractionLayer }
python --version
python -m pip install --upgrade --upgrade-strategy eager pip
pip install --upgrade --upgrade-strategy eager setuptools wheel

if (-not $env:CICD_IMAGE_NAME) {
    pip install --upgrade --upgrade-strategy eager virtualenvwrapper-win
    mkvirtualenv $VirtualEnvironment
}

$UseExitCode = 0
try {
    $env:GIT_PYTHON_REFRESH = "quiet"
    if ($env:PIP_INSTALLS) { pip install --upgrade $env:PIP_INSTALLS }
    if ($env:PIP_INSTALL_FILE) { pip install --upgrade --requirement $env:PIP_INSTALL_FILE }
    if ($env:PRE_SCRIPT) { $env:PRE_SCRIPT }
    python $env:CICD_SUPPORT_SCRIPTS\$env:ACTION.py
    if ($env:POST_SCRIPT) { $env:POST_SCRIPT }
} finally {
    $UseExitCode = $LASTEXITCODE
    if (-not $env:CICD_IMAGE_NAME) { rmvirtualenv $VirtualEnvironment }
}
Exit $UseExitCode
