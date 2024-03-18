Param( [Parameter(Mandatory=$true)][Alias('I')][string]$Item, [Alias('S')][string]$Suffix )
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Reset common variables
$env:CICD_SUPPORT_SCRIPTS=""
$env:CI_PROJECT_NAMESPACE=""
$env:CI_PROJECT_NAME=""
$env:CI_PROJECT_ID=""
$env:GCP_KEY_development=""

$env:CICD_SUPPORT_SCRIPTS="$env:USERPROFILE\git\ALMTools\bart-images\cicd-scripts"

$env:ANSIBLE_SUPPORT="$env:CICD_SUPPORT_SCRIPTS/../ansible"
$env:ANSIBLE_INVENTORY="$env:ANSIBLE_SUPPORT/hosts"
$env:ANSIBLE_ROLES_PATH="$env:ANSIBLE_SUPPORT/roles"
$env:ANSIBLE_LIBRARY="$env:ANSIBLE_SUPPORT/plugins"
$env:ARTIFACTORY_URL="https://oncenter.jfrog.io/artifactory"
$env:CI_COMMIT_SHORT_SHA="0"
$env:CI_ENVIRONMENT_NAME=$env:USERNAME
$env:CI_SERVER_HOST="gitlab.buildone.co"
$env:CI_SERVER_URL="https://$env:CI_SERVER_HOST"
$env:CI_API_V4_URL="$env:CI_SERVER_URL/api/v4"
$env:CI_BUILD_ARTIFACTS="artifacts"
$env:CI_TEST_RESULTS="test_results"
$env:GITLAB_USER_LOGIN=$env:USERNAME
$env:NO_REMOTE_DOCKER_REGISTRY=$true
$env:NO_REMOTE_ARTIFACT_STORAGE=$true
$env:NO_BUILD_TAGGING=$true
$env:USER=$env:USERNAME
$env:HOME=$env:USERPROFILE
If (Test-Path cicd-support\Set-ProjectVars.ps1) { cicd-support\Set-ProjectVars.ps1 }
& $env:USERPROFILE\.ssh\Set-UserAuth.ps1
python $env:CICD_SUPPORT_SCRIPTS\$Item.py $Suffix
