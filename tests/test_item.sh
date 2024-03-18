if [ -z "$1" ]; then echo "usage: $0 function"; exit 1; fi
item=$1

# Reset common variables
export CICD_SUPPORT_SCRIPTS=""
export CI_PROJECT_NAMESPACE=""
export CI_PROJECT_NAME=""
export CI_PROJECT_ID=""
export GCP_KEY_development=""

export CICD_SUPPORT_SCRIPTS="$HOME/git/ALMTools/bart-images/cicd-scripts"

export ANSIBLE_SUPPORT="$CICD_SUPPORT_SCRIPTS/../ansible"
export ANSIBLE_ROLES_PATH="$ANSIBLE_SUPPORT/roles"
export ANSIBLE_LIBRARY="$ANSIBLE_SUPPORT/plugins"
export ARTIFACTORY_URL="https://oncenter.jfrog.io/artifactory"
export CI_COMMIT_SHORT_SHA="0"
export CI_ENVIRONMENT_NAME=$USER
export CI_SERVER_HOST="gitlab.buildone.co"
export CI_SERVER_URL="https://$CI_SERVER_HOST"
export CI_API_V4_URL="$CI_SERVER_URL/api/v4"
export CI_BUILD_ARTIFACTS="artifacts"
export CI_TEST_RESULTS="test_results"
export GITLAB_USER_LOGIN=$USER
export NO_REMOTE_DOCKER_REGISTRY=true
export NO_REMOTE_ARTIFACT_STORAGE=true
export NO_BUILD_TAGGING=true
if [ -e cicd-support/set_project_vars.sh ]; then source cicd-support/set_project_vars.sh; fi
source ~/.ssh/set_user_auth.sh
python $CICD_SUPPORT_SCRIPTS/$item.py $2
