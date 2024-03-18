# GitLab variables
$env:CI_PROJECT_NAMESPACE="cc/sre"
$env:CI_PROJECT_NAME="bart-images"
$env:CI_PROJECT_ID="870"
if ($env:CI_ENVIRONMENT_NAME -eq "") { $env:CI_ENVIRONMENT_NAME="devlocal" }

# Windows variables
$env:USER=$env:USERNAME
$env:HOME=$env:USERPROFILE

# Authentication variables
$SshDir="$env:HOME/.ssh"
$env:GOOGLE_APPLICATION_CREDENTIALS="$SshDir/gcp_devbuilder.json"
$env:GCP_KEY_development=$env:GOOGLE_APPLICATION_CREDENTIALS

# Project specific variables
$env:CICD_SUPPORT_SCRIPTS="cicd-scripts"
