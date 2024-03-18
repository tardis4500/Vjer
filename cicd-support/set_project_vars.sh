# GitLab variables
export CI_PROJECT_NAMESPACE="cc/sre"
export CI_PROJECT_NAME="bart-images"
export CI_PROJECT_ID="870"
if [ -z "$CI_ENVIRONMENT_NAME" ]; then export CI_ENVIRONMENT_NAME="devlocal"; fi

# Authentication variables
SshDir="$HOME/.ssh"
export GOOGLE_APPLICATION_CREDENTIALS="$SshDir/gcp_devbuilder.json"
export GCP_KEY_development="$GOOGLE_APPLICATION_CREDENTIALS"

# Project specific variables
export CICD_SUPPORT_SCRIPTS="cicd-scripts"
