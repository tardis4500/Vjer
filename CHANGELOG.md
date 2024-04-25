# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Current Release

### [36.0.0] - 2024-04-25

- Changed
  - Don't replace periods in tags. (GitHub #16)

## Release History

### [35.0.0] - 2024-04-25

- Changed
  - Remove bad characters for Helm versions. (GitHub #15)

### [34.2.0] - 2024-04-22

- Changed
  - Sanitize Docker tags and Helm versions. (GitHub #14)

### [34.1.1] - 2024-04-19

- Added
  - Report the Google SDK version. (GitHub #13)

### [34.1.0] - 2024-04-19

- Changed
  - Convert extra Helm versions on pre_release to lowercase. (GitHub #12)

### [34.0.0] - 2024-04-18

- Added
  - Added integration testing. (GitHub #10)

- Changed
  - Remove need to specify artifact_repo in config file. (GitHub #11)
  - Rename config values docker_repo to container_registry and help_repo to helm_repository.

### [33.0.1] - 2024-04-18

- Changed
  - Switched flit to be a required module. (GitHub #9)

### [33.0.0] - 2024-04-18

- Added
  - Added support for multiple Docker tags and Helm versions at build. (GitHub #8)

- Changed
  - Required specification of full Docker and Helm repo info in config file.

### [32.1.0] - 2024-04-11

- Changed
  - Cleanup version output and add --version option. (GitHub #5)
  - Fix tagging on release. (GitHub #7)

### [32.0.0] - 2024-04-10

- Added
  - Added flit and bumpver support. (GitHub #2)

- Removed
  - Removed implicit release steps. (GitHub #6)

### [31.0.0] - 2024-03-21

- Added
  - Added bumpver version service. (GitHub #3)
  - Added python test types: flake8, pylint, and mypy. (GitHub #3)
  - Added __main__.py to enable module execution. (GitHub #4)

- Changed
  - Improved version code. (GitHub #4)
  - Report any OS. (GitHub #4)
  - Changed project.product to project.name. (GitHub #4)

- Removed
  - Removed semver version service. (GitHub #4)

### [30.0.0] - 2024-03-20

- Changed
  - Converted to installable module. (GitHub #1)

- Removed
  - Removed support for all action types except Docker and Helm.

### [29.2.0] - 2023-09-08

- Added
  - Added .NET 2.2 SDK to the Windows image. (SRE-11494)
  - Added Git to the Windows image.

### [29.1.0] - 2023-08-23

- Changed
  - Converted the JAMS role modules to PowerShell. (SRE-11375)

### [29.0.0] - 2023-08-22

- Added
  - Added new scan and dotnet images. (SRE-11203)
  - Added the coco_gcp_container_cluster and coco_gcp_container_node_pool modules. (SRE-11268)

- Changed
  - Improved builds by creating a base image. (SRE-11203)

- Removed
  - Removed the DotNet 5 SDK, DotNet EF, and Terraform. (SRE-11203)

### [28.1.1] - 2023-08-08

- Changed
  - Fixed the release.release_increment_release method. (SRE-11315)

### [28.1.0] - 2023-08-01

- Added
  - Added the load_balancer role. (SRE-11279)

### [28.0.5] - 2023-07-17

- Changed
  - Perform Helm update on all remote Helm deployments. (SRE-11197)

### [28.0.4] - 2023-07-12

- Changed
  - Fix deployer builder for kubetastic components. (SRE-11175)

### [28.0.3] - 2023-07-11

- Changed
  - Restrict all Helm staging and production deployments to remote charts. (SRE-11168)

### [28.0.2] - 2023-07-11

- Changed
  - Add Ansible support. (SRE-11160)

### [28.0.1] - 2023-07-07

- Changed
  - Fix release stage. (SRE-11144)

### [28.0.0] - 2023-07-06

- Added
  - Added support for building higher environment deployers. (SRE-11016)
  - Added a deployment image. (SRE-11020)
  - Added support for creating a JIRA ticket to request a staging deploy. (SRE-11042)
  - Added tooling for code scans. (SRE-11064)

- Changed
  - Used new Python language features from 3.7 thru 3.10. (SRE-10981)
  - Applied Google coding standards including type checking. (SRE-10985)
  - Upgrade to Python 11.

### [27.1.1] - 2023-05-18

- Added
  - Added missing JAMS host servers to jams role. (SRE-10946)

### [27.1.0] - 2023-05-18

- Added
  - Added the deploy_product task to the coco role. (SRE-10772)
  - Added a backup_artifact_target option to the jfrog download_artifacts task. (SRE-10803)
  - Added the win_process and win_process_info modules to the Ansible coco role. (SRE-10817)
  - Added the jams role to control JAMS jobs. (SRE-10860)
  - Added docker variables to coco role. (SRE-10887)
  - Added get_environment_value to coco role. (SRE-10912)

### [27.0.1] - 2023-05-03

- Added
  - Install sshpass to linux container for Ansible deployments. (SRE-10877)

- Changed
  - Fix build number compare in qb_deploy. (SRE-10866)
  - Provide method to ignore target environment for qb_deploy. (SRE-10866)

### [27.0.0] - 2023-04-11

- Removed
  - Removed the default Ansible inventory. (SRE-10761)
  - Removed the publish stage. (SRE-10755)

### [26.0.0] - 2023-04-04

- Added
  - Added support for reading version out of environment. (SRE-10740)

- Changed
  - Updated Ansible P2 inventory variables to match ConfigLib. (SRE-10603)

- Removed
  - Moved BaRT CI/CD templates to another repo. (SRE-10675)

### [25.0.0] - 2023-03-22

- Added
  - Added coco and jfrog Ansible roles. (SRE-10515)
  - Added deployment for msbuild workflow. (SRE-10517)
  - Added QuickBuild deployment support. (SRE-10670)

- Changed
  - Moved repo related variables to the CI environment. (SRE-10502)
  - Use project version as default for remote Helm chart deployment. (SRE-10503)
  - Improved CI/CD template names. (SRE-10605)

### [24.1.3] - 2023-02-17

- Changed
  - Bad CI_COMMIT_BRANCH fix in release 6.1.2. (SRE-10512)

### [24.1.2] - 2023-02-17

- Changed
  - Fixed CI_COMMIT_BRANCH failure on merge request. (SRE-10512)

### [24.1.1] - 2023-02-14

- Changed
  - Fixed template reference. (SRE-10499)
  - Update Windows project file on release.

### [24.1.0] - 2023-02-14

- Added
  - Added support for Staging2 and Production2. (SRE-10496)

### [24.0.1] - 2023-02-13

- Changed
  - Don't require pyodbc on Linux. (SRE-10151)

### [24.0.0] - 2023-02-13

- Added
  - Added support for storing artifacts to JFrog. (SRE-10151)
  - Added Sencha. (SRE-10424)
  - Added copy method to publish step. (SRE-10427)
  - Added build_info_db publish step. (SRE-10455)

- Changed
  - Changed the bucket storage to OnCenter JFrog. (SRE-10151)
  - Improved workflows and added additional controls.

### [23.0.2] - 2023-01-26

- Changed
  - Don't create release or deploy stages on merge requests. (SRE-10407)

### [23.0.1] - 2023-01-26

- Changed
  - Don't create release or deploy stages on merge requests. (SRE-10407)
  - Don't merge request test from release branch to release/latest.

### [23.0.0] - 2023-01-25

- Added
  - Added Helm rollback support. (SRE-10243)
  - Added rollback stages for higher environments. (SRE-10353)
  - Added msbuild support. (SRE-10368)
  - Added a Windows container. (SRE-10382)

- Changed
  - Update workflows for new GitLab deployment strategy. (SRE-10351)

- Removed
  - Removed publish stage from standard workflow.

### [22.0.2] - 2023-01-09

- Changed
  - Update GitLab server certificate. (SRE-10321)

### [22.0.1] - 2022-12-08

- Changed
  - Fixed pre-release stage in app workflow. (SRE-10220)

### [22.0.0] - 2022-12-07

- Added
  - Added POST_SCRIPT to base job support. (SRE-10217)
  - Added exec deploy method. (SRE-10217)

- Changed
  - Inhibit pre-release stage in app workflow. (SRE-10217)

### [21.0.1] - 2022-11-29

- Changed
  - Fix JFrog Docker tagging on release. (SRE-10158)

### [21.0.0] - 2022-11-29

- Changed
  - Use a multi-stage Dockerfile. (SRE-10153)
  - Changed default Helm chart directory name to helm-chart. (SRE-10156)

### [20.0.0] - 2022-11-23

- Added
  - Added JFrog support for storing artifacts. (SRE-10144)
  - Added default for Docker registry.

- Changed
  - Fixed up environment list. (SRE-10119)
  - Load all Python requirements for all actions in the base image. (SRE-10120)
  - Updated default runner. (SRE-10121)
  - Moved source repo. (SRE-10143)

### [19.0.0] - 2022-11-07

- Added
  - Added GitLab CI/CD templates. (SRE-10060)
  - Added build of docker image for GitLab runner. (SRE-10059)

### [18.2.0] - Unreleased

- Added
  - Added build version injection to the Docker build. (DOP-3421)

<!-- This comment should inhibit merge conflicts between branches -->

### [18.1.1] - 2022-09-26

- Changed
  - Fix bad template file name. (DOP-3402)

### [18.1.0] - 2022-09-26

- Added
  - Added primary/secondary environments for dev/qa. (DOP-3392)

- Changed
  - Refactored GitLab templates to offer better orthogonality and control.

### [18.0.0] - 2022-09-22

- Added
  - Added support for using other CI variables as build numbers. (DOP-3323)
  - Added publish action to support build tagging. (DOP-3324)
  - Add Helm template to Helm test phase. (DOP-3376)

- Changed
  - Upgrade Python to 3.10. (DOP-3384)
  - Updated tags to use new VM runners.
  - Prevent concurrent deployments to the same environment.
  - Don't initialize the Git client if no local repo found.

### [17.2.1] - 2022-08-17

- Changed
  - Install the new Google Kubernetes auth plugin but leave deactivated. (DOP-2995)
  - Update components. (DOP-3254)

### [17.2.0] - 2022-08-02

- Added
  - Added support for package deployment. (DOP-3197)

- Changed
  - Pin kubectl version and add kubectl version reporting. (DOP-3160)

### [17.1.3] - 2022-07-14

- Changed
  - Updated Python and dependencies. (DOP-3111)

### [17.1.2] - 2022-04-26

- Changed
  - Fixed Ansible values file handling. (DOP-2834)

### [17.1.1] - 2022-04-13

- Changed
  - Strip UTF-8 BOM from .Net EF migration SQL scripts. (DOP-2805)

### [17.1.0] - 2022-04-08

- Added
  - Added the .Net 3.1 SDK. (DOP-2760)

### [17.0.2] - 2022-04-04

- Changed
  - Upgraded Python to 3.9.12. (DOP-2750)

### [17.0.1] - 2022-03-17

- Changed
  - Fix builds that rely on the filecopy build method. (DOP-2717)

### [17.0.0] - 2022-03-16

- Changed
  - Replaced sql_script types with generic file types. (DOP-2712)

### [16.3.2] - 2022-03-15

- Changed
  - Fix Ansible linting error in GCP role. (DOP-2685)
  - Update components. (DOP-2685)
  - Report all .NET SDK versions.

### [16.3.1] - 2022-02-15

- Changed
  - Install .Net 5.0 SDK to container. (DOP-2573)
  - Set the default .Net version to 6.0. (DOP-2573)

### [16.3.0] - 2022-02-11

- Added
  - Added Ansible rollback support. (DOP-2569)

- Changed
  - Upgraded DotNet SDK to 6.0. (DOP-2565)

### [16.2.1] - 2022-02-03

- Changed
  - Fixed Python junit test generation. (DOP-2555)

### [16.2.0] - 2022-01-31

- Added
  - Added support for Terraform -refresh-only. (DOP-2533)

### [16.1.0] - 2022-01-24

- Added
  - Added pywinrm for deployment. (DOP-2523)

- Changed
  - Upgraded Python to 3.9.10. (DOP-2524)
  - Exclude terraform_output.json during Ansible build.

### [16.0.0] - 2022-01-12

- Changed
  - Moved Terraform plan support into the deploy phase. (DOP-2502)

- Removed
  - Removed the process stage. (DOP-2502)

### [15.1.0] - 2022-01-10

- Added
  - Added utils.RemoteStorage. (DOP-2501)
  - Added support for deployment of remote Terraform plans and Ansible playbooks. (DOP-2501)

### [15.0.2] - 2022-01-07

- Changed
  - Need to create directory on Terraform process step. (DOP-2500)

### [15.0.1] - 2022-01-07

- Added
  - Added missing .base-process job for process step support. (DOP-2499)

### [15.0.0] - 2022-01-06

- Added
  - Added support for publishing Terraform plans. (DOP-2490)
  - Added the ProcessStep type to handle special process steps. (DOP-2497)

### [14.6.0] - 2022-01-04

- Changed
  - Stop using -upgrade and -reconfigure on terraform init. (DOP-2491)
  - Add support for storing Terraform outputs. (DOP-2492)

### [14.5.1] - 2021-12-28

- Changed
  - Preserve name of SQL script after pre-release. (DOP-2485)
  - Fix sql_script pre-release when using default extension. (DOP-2486)

### [14.5.0] - 2021-12-21

- Added
  - Added support for other extensions on sql_script release type. (DOP-2483)

### [14.4.2] - 2021-12-08

- Changed
  - Set ANSIBLE_HOST_KEY_CHECKING in container. (DOP-2454)

### [14.4.1] - 2021-11-30

- Changed
  - Fix unexpected SQL script rename on pre-release. (DOP-2445)
  - Allow primary branch to be named "main" and "develop" in addition to "master."

### [14.4.0] - 2021-11-30

- Added
  - Added support for SQL script build and release. (DOP-2444)

### [14.3.0] - 2021-11-23

- Added
  - Added support for different versioning services. (DOP-2432)

### [14.2.3] - 2021-11-18

- Changed
  - Upgrade Python to 3.9.9 and Ansible to 4.8.0. (DOP-2428)

### [14.2.2] - 2021-11-15

- Changed
  - Updated build tools. (DOP-2416)

### [14.2.1] - 2021-10-28

- Changed
  - Fix Docker builds. (DOP-2357)

### [14.2.0] - 2021-10-28

- Changed
  - Upgraded BatCave to the release 40 series. (DOP-2356)
  - Pinned pyparsing module since the release 3 causes issues with Google modules.

### [14.1.3] - 2021-10-26

- Added
  - Add report of primary tool versions. (DOP-2345)

- Changed
  - Use new Python 3.9 dict union operator and removeprefix/removesuffix methods.

### [14.1.2] - 2021-10-21

- Changed
  - Updated Helm and cm-push plugin. (DOP-2331)
  - Fix Helm pre-release failure. (DOP-2337)

### [14.1.1] - 2021-10-15

- Changed
  - Fix Terraform init calls. (DOP-2329)

### [14.1.0] - 2021-10-12

- Added
  - Added Dotnet SDK and EF tools support. (DOP-2317)

### [14.0.1] - 2021-10-07

- Added
  - Added reporting of CI/CD support version on action startup. (DOP-2312)

- Changed
  - Pinned the version of the Helm push plugin due to provider issues. (DOP-2311)

### [14.0.0] - 2021-10-07

- Changed
  - Publish packages to GCP bucket instead of GitLab package repository. (DOP-2309)

### [13.0.0] - 2021-10-06

- Added
  - Added Terraform support. (DOP-2219)
  - Added Rollback support. (DOP-2219)

### [12.2.2] - 2021-09-27

- Changed
  - Fix Helm version for push plugin incompatibility. (DOP-2267)

### [12.2.1] - 2021-09-24

- Added
  - Added openssh-client for Ansible support. (DOP-2263)

### [12.2.0] - 2021-09-08

- Added
  - Added Ansible release support. (DOP-2183)

- Changed
  - Upgrade to Python 3.9.7. (DOP-2184)

### [12.1.1] - 2021-07-30

- Changed
  - Fix Docker image tagging on release. (DOP-2049)

### [12.1.0] - 2021-07-29

- Added
  - Added support for a pre-release phase. (DOP-2018)
  - Set Helm chart appVersion if requested.
  - Added library workflow and python module templates.
  - Added dependency build to Helm test and build.

- Changed
  - Ignore stderr on ansible lint.
  - Treat Helm chart values file as a version file.

### [12.0.0] - 2021-07-20

- Changed
  - Put support scripts in image. (DOP-1780)
  - Upgrade to Python 3.9.6. (DOP-1995)
  - Renamed PYTHON_IMAGE_REPO/TAG to CICD_IMAGE_REPO/TAG.

- Removed
  - Removed need for IS_CICD_SUPPORT_BUILD variable.

### [11.1.0] - 2021-05-27

- Changed
  - Add Helm chart repo to Docker image. (DOP-1782)

### [11.0.1] - 2021-05-26

- Changed
  - Upgraded python and requirements. (DOP-1745)

### [11.0.0] - 2021-05-07

- Added
  - Added test types for Ansible, Docker, and Helm linting. (DOP-1553)
  - Added Ansible role for common GCP values. (DOP-1588)

- Changed
  - Upgraded BatCave to 39 series. (DOP-1391)

### [10.0.0] - 2021-04-22

- Added
  - Added default build runner tag. (DOP-1488)

- Changed
  - Set the default image to the built support image. (DOP-1491)
  - Rename the base job template to .base-job-support. (DOP-1491)

### [9.2.1] - 2021-04-15

- Added
  - Added Docker build log output. (DOP-1423)

### [9.2.0] - 2021-04-15

- Added
  - Added support for Docker build args. (DOP-1421)

### [9.1.1] - 2021-04-13

- Changed
  - Update Python to 3.8.9. (DOP-1388)
  - Fix Helm package name during release. (DOP-1403)

### [9.1.0] - 2021-03-30

- Added
  - Added support for PyPi package release publishing. (DOP-1363)

### [9.0.2] - 2021-03-25

- Changed
  - Update Helm repo fqdn. (DOP-1340)

### [9.0.1] - 2021-03-18

- Changed
  - Fixed stage typo. (DOP-1308)

### [9.0.0] - 2021-03-18

- Changed
  - Changed environment names to lowercase. (DOP-1307)
  - Always used full environment names. (DOP-1307)

- Removed
  - Remove redundant Helm step namespace value.

### [8.0.0] - 2021-03-17

- Added
  - Added support for multiple Helm values files. (DOP-373)
  - Added support for deploying remote Helm charts. (DOP-1298)

### [7.0.0] - 2021-03-15

- Changed
  - Use pre-built image for Python actions. (DOP-1223)
  - Make release actions the same as build and deploy.

- Removed
  - Remove helm-template as obsolete as Helm is baked into image. (DOP-1223)

### [6.2.2] - 2021-03-10

- Changed
  - Moved build runner to GKE. (DOP-880)

### [6.2.1] - 2021-03-03

- Changed
  - Force Helm release name to lowercase. (DOP-1260)

### [6.2.0] - 2021-03-03

- Changed
  - Fixed Pylance linting issues.
  - Pin BatCave to the major release version 38.
  - Allow project config to specify the Helm release name. (DOP-1257)

### [6.1.4] - 2021-02-18

- Changed
  - Fixed broken ansible builds. (DOP-1232)

### [6.1.3] - 2021-02-15

- Changed
  - Fixed broken filecopy builds. (DOP-1215)

### [6.1.2] - 2021-02-12

- Changed
  - Show command line commands when run. (DOP-1206)

### [6.1.1] - 2021-02-09

- Changed
  - Use the Helm --create-namespace command where applicable. (DOP-1203)
  - Don't create namespace when building a Helm chart.

### [6.1.0] - 2021-02-09

- Added
  - Added support for specifying the Dockerfile and image names. (DOP-1198)
  - Added support for python module builds. (DOP-1199)
  - Added support for running pre-build tests. (DOP-1200)

- Changed
  - Switch to Buster slim image for Python support. (DOP-1163)
  - Don't try execute steps if not defined.

### [6.0.0] - 2021-02-05

- Added
  - Added support for docker builds. (DOP-377)
  - Added support for ansible and kubernetes build and deploy. (DOP-377)
  - Added Google Cloud SDK to build image.

### [5.2.2] - 2020-10-23

- Changed
  - Ignore stderr on Helm commands. (DOP-949)

### [5.2.1] - 2020-09-23

- Changed
  - Workaround a bug in BatCave that tries to create an existing branch.

### [5.2.0] - 2020-06-24

- Changed
  - Define SUPPORT_HOME in addition to support root.
  - Install pip modules from SUPPORT_HOME/requirements.txt.

### [5.1.0] - 2020-06-23

- Added
  - Added support for overwrite flag on filecopy deploy method.

### [5.0.2] - 2020-06-23

- Changed
  - Fixed usage of artifacts in filecopy deploy method.

### [5.0.1] - 2020-06-05

- Removed
  - Removed GIT_STRATEGY of None on deploy to get cicd-support.

### [5.0.0] - 2020-05-28

- Added
  - Added DevOps environment. (DOP-468)
  - Added base workflow template.
  - Added support for globs in filecopy build artifacts. (DOP-410)
  - Added filecopy deploy support. (DOP-410)

- Changed
  - Converted to new GitLab rules syntax.
  - Better error message when build or deploy type not found.
  - Converted project configuration to YAML. (DOP-410)

### [4.0.1] - 2020-05-05

- Changed
  - Use FQDN for database manager host. (DOP-446)

### [4.0.0] - 2020-03-23

- Changed
  - Add more Helm deploy control. (DOP-313)

### [3.0.1] - 2020-03-18

- Changed
  - Fixed GitLab Releases API URL generation. (DOP-369)

### [3.0.0] - 2020-03-17

- Added
  - Add Helm chart template. (DOP-338)
  - Added Helm chart build support. (DOP-362)

### [2.1.1] - 2020-03-06

- Changed
  - Fix release program.

### [2.1.0] - 2020-03-06

- Added
  - Added filecopy build type. (DOP-302)

### [2.0.0] - 2020-03-04

- Added
  - Added build support. (DOP-308)
  - Added utils module. (DOP-308)

- Changed
  - Converted release.py to use new utils module. (DOP-308)

### [1.0.1] - 2020-02-26

- Added
  - Added CHANGELOG.

- Changed
  - Check for existence of Helm package in build. (DOP-297)
  - Need to get the remote release script. (DOP-297)
  - Fixed project root when using from other repo. (DOP-297)
  - Support releases with other than three digits. (DOP-297)
  - Improved README.

### [1.0.0] - 2020-02-25

- Initial release of re-architecture.

### [Pi.P14] - 2019-09-26

- Changed
  - Upgraded halpy to 36.3.1. (DO-2533)

### [Pi.P13] - 2019-09-19

- Changed
  - Upgraded ant to 1.10.7. (DO-2442)
  - Upgraded Docker to 19.03.2. (DO-2442)
  - Upgraded dotCover to 2019.2.2. (DO-2442)
  - Upgraded Windows Git to 2.23.0. (DO-2442)
  - Upgraded Google Cloud SDK to 263.0.0. (DO-2442)
  - Upgraded halpy to 36.3.0. (DO-2348, DO-2442)
  - Upgraded JRE/JDK to 1.8.0_221. (DO-2442)
  - Upgraded kubectl to 1.16.0. (DO-2442)
  - Upgraded maven to 3.6.2. (DO-2442)
  - Upgraded MSBuild Tools to 15.9.16. (DO-2442)
  - Upgraded nginx to 1.16.3. (DO-2442)
  - Upgraded nuget to 5.2.0. (DO-2442)

### [Pi.P12] - 2019-07-25

- Added
  - Added dotCover 2019.1.3. (DO-2224)
  - Added NUnit 2.6.4. (DO-2224)

- Changed
  - Upgraded halpy to 36.2.0. (DO-2224, DO-2260)

### [Pi.P11] - 2019-07-15

- Changed
  - Upgraded halpy to 36.1.1. (DO-2206)

### [Pi.P10] - 2019-07-12

- Changed
  - Upgraded halpy to 36.1.0. (DO-2185)

### [Pi.P09] - 2019-07-05

- Changed
  - Upgraded halpy to 36.0.0. (DO-2162)
  - Upgraded docker to 18.09.7. (DO-2164)
  - Upgraded gcloud to 253.0.0. (DO-2164)
  - Upgraded kubectl to 1.15.0. (DO-2164)
  - Upgraded MSBuild Tools to 15.9.13. (DO-2164)

### [Pi.P08] - 2019-06-17

- Changed
  - Need to perform yum clean to workaround IUP repo change. (DO-2044)
  - Don't set npm_registry_config for node deploy servers. (DO-2010)
  - Upgraded halpy to 35.1.0. (DO-1989)
  - Upgraded ant to 1.10.6. (DO-2044)
  - Upgraded docker to 18.09.6. (DO-2044)
  - Upgraded gcloud to 250.0.0. (DO-2044)
  - Upgraded git on Windows to 2.22.0. (DO-2044)
  - Upgraded kubectl to 1.42.3. (DO-2044)
  - Upgraded pm2 to 3.5.1. (DO-2044)
  - Upgraded python to 3.6.8. (DO-2044)
  - Upgraded nuget to 5.0.2. (DO-2044)

### [Pi.P07] - 2019-05-08

- Changed
  - Upgraded halpy to 35.0.0. (DO-1844, DO-1927)
  - Upgraded gcloud to 244.0.0. (DO-1815)
  - Upgraded JRE to 1.8.0_211. (DO-1936)
  - Upgraded nginx to 1.16.2. (DO-1160)
  - Upgraded pm2 to 3.5.0. (DO-1160)

### [Pi.P06] - 2019-04-25

- Changed
  - Upgraded halpy to 34.0.0. (DO-1866, DO-1876)

### [Pi.P05] - 2019-04-17

- Added
  - Added .NET Framework 4.6.2 targeting pack. (DO-1818)

- Changed
  - Upgraded docker to 18.09.5. (DO-1815)
  - Upgraded gcloud to 241.0.0. (DO-1815)
  - Upgraded halpy to 33.1.0. (DO-1814, DO-1817)
  - Upgraded kubectl to to 1.14.1. (DO-1815)
  - Upgraded MSBuild Tools to 15.9.11. (DO-1815)

### [Pi.P04] - 2019-04-05

- Changed
  - Don't manage firewall if not installed. (DO-1791)
  - Add --proxy argument. (DO-1792)
  - Fix the umask for node deployment. (DO-1795)

### [Pi.P03] - 2019-03-27

- Changed
  - Fixed minor issue with service_user name caching.
  - Fixed issue with redundant config table on reinstall. (DO-1762)
  - Upgraded gcloud to 239.0.0. (DO-1759)
  - Upgraded halpy to 33.0.2. (DO-1759)
  - Upgraded MSBuild Tools to 15.9.10. (DO-1759)
  - Upgraded nuget to 4.9.4. (DO-1759)
  - Upgraded SQL ODBC driver to 17.3. (DO-1759)

### [Pi.P02] - 2019-03-25

- Changed
  - Fix permissions on Linux bart shell script and node module installs. (DO-1729)
  - Removed fixup of /opt directory now that node apps will be deployed in user home. (DO-1716)
  - Upgraded halpy to 33.0.1. (DO-1739)
  - Improved --no-qb handling. (DO-1758)

- Removed
  - Removed --no-service-management argument to work around DO-1623.

### [Pi.P01] - 2019-03-06

- Added
  - Added --no-service-management argument to work around DO-1623.

- Changed
  - Don't setup service account if --no-qb. (DO-1307)
  - Updated for halpy snake case changes. (DO-1450)
  - Added known_hosts file to ssh keys package. (DO-1577)
  - Use property decorators. (DO-1509)
  - Upgraded docker to 18.09.3.
  - Upgraded gcloud to 236.0.0.
  - Upgraded git to 2.21.0.
  - Upgraded kubectl to 1.13.4.
  - Upgraded halpy to 33.0.0.

### [Pi] - 2019-02-20

--------------

- Changed
  - Added node to Windows build configuration. (DO-1295)
  - Added iis to Windows deploy configuration. (DO-1297)
  - Added libffi-devel to support Python build. (DO-1340)
  - Move SQLDB and SSDT to Visual Studio installed. (DO-1543)
  - Upgraded halpy to 32.0.0. (DO-926)
  - Use snake_case. (DO-1450)
  - Updates to respond to halpy changes.
  - Spelling cleanup.
  - Upgraded docker to 18.09.2.
  - Upgraded gcloud to 234.0.0.
  - Upgraded jre and jdk to 1.8.0_201.
  - Upgraded kubectl to 1.13.3.
  - Upgraded MSBuild Tools to 15.9.7.
  - Upgraded nuget to 4.9.3.
  - Upgraded SQL DB Tools to 15.9.7.

### [Omicron.P03] - 2019-01-14

- Added
  - Added mesa-libGL to Linux base packages for HAL runtime. (DO-1329)

- Changed
  - Fixed CentOS 6 installation issue. (DO-1364)
  - Upgraded halpy to 31.0.0. (DO-1322)
  - Upgraded docker to 18.09.1.
  - Upgraded gcloud to 229.0.0.
  - Upgraded kubectl to 1.13.2.
  - Upgraded nuget to 4.9.2.

### [Omicron.P02] - 2019-01-09

--

- Changed
  - Upgraded halpy to 30.0.3. (DO-1351)

### [Omicron.P01] - 2019-01-02

--

- Changed
  - Fixed Bitbucket ssh key. (DO-1136)
  - Fixed update handling. (DO-1309)

### [Omicron] - 2018-12-21

-
- Added
  - Added --no-qb option for installing on user workstation. (DO-1049)
  - Added Google Cloud configuration for docker authorization. (DO-1125)
  - Moved BaRT support commands from halpy. (DO-1107)

- Changed
  - Update command parsing for new halpy.commander.Commander() handler. (DO-1077)
  - Upgraded halpy to 30.0.2. (DO-1077)
  - Upgraded Docker to 18.09. (DO-1160)
  - Upgraded Google Cloud SDK to 228.0.0. (DO-1160)
  - Upgraded kubectl to 1.13.1. (DO-1160)
  - Upgraded Maven to 3.6.0. (DO-1160)
  - Upgraded MSBuild Tools to 15.9.4. (DO-1160)
  - Upgraded Nginx to 1.14.2. (DO-1160)
  - Upgraded NuGet to 4.8.1. (DO-1160)
  - Upgraded SQL DB Tools to 15.9.4. (DO-1160)

### [Xi.P03] - 2018-11-29

- Changed
  - Upgraded halpy to 29.1.1. (DO-1180)

### [Xi.P02] - 2018-11-28

- Changed
  - Upgraded halpy to 29.1.0. (DO-1170)

### [Xi.P01] - 2018-11-20

- Changed
  - Upgraded halpy to 29.0.2. (DO-1138)

### [Xi] - 2018-10-31

- Added
  - Add BoxBuilder types. (DO-89)
  - Cache install options. (DO-1015)

- Changed
  - Upgraded Ant to 1.10.5. (DO-949)
  - Upgraded Windows Git to 2.19.1. (DO-949)
  - Upgraded Google Cloud SDK to 222.0.0. (DO-949)
  - Upgraded kubectl to 1.12.2. (DO-949)
  - Upgraded Windows JRE to 1.8.0_192. (DO-949)
  - Upgraded MSBuild Tools to 15.8.8. (DO-949)
  - Upgraded NuGet to 4.7.1. (DO-949)
  - Upgraded pm2 to 2.10.4. (DO-949)
  - Upgraded SQL DB Tools to 15.8.8. (DO-949)
  - Upgraded SQL ODBC driver to 17.2. (DO-949)

- Removed
  - Removed node support from Windows. (DO-927)
  - Removed SQL command line tools. (DO-949)

### [Nu.P30] - 2018-10-24

- Changed
  - Upgraded halpy to 29.0.1. (DO-1016)

### [Nu.P29] - 2018-10-22

- Changed
  - Upgraded nitro to 1.0.1. (DO-982)

### [Nu.P28] - 2018-10-22

- Changed
  - Upgraded halpy to 29.0.0. (DO-1002)

### [Nu.P27] - 2018-10-10

- Changed
  - Upgraded halpy to 28.0.4. (DO-976)

### [Nu.P26] - 2018-10-08

- Changed
  - Upgraded halpy to 28.0.3. (DO-967)

### [Nu.P25] - 2018-10-05

- Changed
  - Upgraded halpy to 28.0.2. (DO-938)

### [Nu.P24] - 2018-09-27

- Changed
  - Upgraded halpy to 28.0.0. (DO-922)

### [Nu.P23] - 2018-09-24

- Changed
  - Upgraded halpy to 27.3.0. (DO-916)

### [Nu.P22] - 2018-09-19

- Changed
  - Upgraded halpy to 27.2.0. (DO-887)

### [Nu.P21] - 2018-08-24

- Changed
  - Upgraded halpy to 27.0.0. (DO-762, DO-763, DO-801)

### [Nu.P20] - 2018-08-08

- Changed
  - Upgraded halpy to 26.4.3. (DO-715)

### [Nu.P19] - 2018-08-08

- Changed
  - Upgraded halpy to 26.4.2. (DO-713)

### [Nu.P18] - 2018-08-08

- Changed
  - Upgraded halpy to 26.4.1. (DO-665, DO-666)

### [Nu.P17] - 2018-08-01

- Changed
  - Improve Python module version checking. (DO-648)
  - Upgraded halpy to 26.4.0. (DO-646)

### [Nu.P16] - 2018-07-013

- Changed
  - Upgraded halpy to 26.3.0. (DO-614)

### [Nu.P15] - 2018-07-012

- Changed
  - Upgraded halpy to 26.2.0. (DO-603)

### [Nu.P14] - 2018-07-011

- Changed
  - Upgraded halpy to 26.1.3. (DO-600)

### [Nu.P13] - 2018-07-09

- Changed
  - Upgraded halpy to 26.1.2. (DO-591)

### [Nu.P12] - 2018-07-09

- Changed
  - Upgraded halpy to 26.1.1. (DO-591)

### [Nu.P11] - 2018-07-05

- Changed
  - Upgraded ant to 1.10.4. (DO-588)
  - Upgraded halpy to 26.1.0. (DO-588)

### [Nu.P10] - 2019-07-02

- Changed
  - Upgraded halpy to 26.0.1. (DO-576)
  - Updated to use new halpy.servermgr.Server() class. (DO-577)

### [Nu.P09] - 2019-06-29

- Changed
  - Upgraded halpy to 26.0.0. (DO-534)
  - Upgraded Google Cloud SDK to 207.0.0.
  - Upgraded MSBuild Tools to 15.7.4.
  - Upgraded Maven to 3.5.4.
  - Upgraded Windows Git to 2.18.0.

### [Nu.P08] - 2018-06-06

- Changed
  - Upgraded halpy to 25.0.1. (DO-525)

### [Nu.P07] - 2018-06-06

- Changed
  - Upgraded halpy to 25.0.0. (DO-338, DO-521)

### [Nu.P06] - 2018-06-05

- Added
  - Added ant support. (DO-482)

- Changed
  - Upgraded halpy to 24.0.1. (DO-465, DO-467, DO-520)
  - Upgraded Google Cloud SDK to 203.0.0. (DO-508)
  - Upgraded MSBuild Tools to 15.7.3. (DO-508)
  - Upgraded MSData Tools to 10.0.61804.210. (DO-508)
  - Upgraded Windows Git to 2.17.1(2). (DO-508)

### [Nu.P05] - 2018-05-07

- Changed
  - Attempt to unlock yum installs before install.
  - Ignore stderr on yum makecache fast.
  - Use yum versionlock on Linux26x86_64 but clear instead of delete.
  - Upgraded halpy to 23.0.0. (DO-423)
  - Upgraded Python to 3.6.5. (DO-423)
  - Upgraded Windows Git to 2.17.0. (DO-423)
  - Upgraded Google Cloud SDK to 199.0.0. (DO-423)
  - Upgraded Node to 8.11.1. (DO-423)
  - Upgraded MSBuild Tools to 15.6.7. (DO-423)

### [Nu.P04] - 2018-04-25

- Changed
  - Upgraded halpy to 22.2.2. (DO-432)

### [Nu.P03] - 2018-04-25

- Changed
  - Upgraded halpy to 22.2.1. (DO-432)

### [Nu.P02] - 2018-04-24

- Changed
  - Upgraded halpy to 22.2.0. (DO-436)

### [Nu.P01] - 2018-04-20

- Changed
  - Downgraded Node to 8.9.4. (DO-415)

### [Nu] - 2018-04-19

- Added
  - Added tools needed to build Visual Studio Database projects. (DO-348)

- Changed
  - Converted to frozen executable. (DO-140)
  - Update schema for better install control. (DO-379)
  - Converted Linux install model to the one used by Windows. (DO-380)
  - Improved installation. (DO-382)
  - Get all versions from product database. (DO-383)
  - Upgraded Node to 8.11.1. (DO-353)
  - Upgraded Google Cloud SDK to 197.0.0. (DO-367)
  - Upgraded MSBuild to 2017 15.6.6. (DO-367)
  - Upgraded nuget to 4.6.2. (DO-367)
  - Upgraded halpy to 22.1.5. (DO-393)
  - Updates to support pip 10. (DO-367)

### [Mu.P04] - 2018-04-13

- Changed
  - Upgraded halpy to 22.1.0. (DO-391)

### [Mu.P03] - 2018-03-21

- Changed
  - Upgraded halpy to 22.0.0. (DO-331)
  - Fix python scripts for BART_HOME location. (DO-333)
  - Upgraded Google Cloud SDK to 195.0.0.
  - Upgraded Docker to 18.03.

### [Mu.P02] - 2018-03-20

- Changed
  - Keep pip up to date. (DO-325)
  - Upgraded halpy to 20.0.0. (DO-289)

### [Mu.P01] - 2018-03-16

- Changed
  - Upgraded halpy to 19.0.2. (DO-319)

### [Mu] - 2018-03-14

--------------

- Changed
  - Upgraded halpy to 19.0.1. (DO-269)
  - Upgraded Git to 2.16.2. (DO-269)
  - Upgraded Google Cloud SDK to 192.0.0. (DO-269)
  - Upgraded MSBuild and MSTest to 2017 15.6.2. (DO-269)

### [Lambda.P05] - 2018-02-21

-

- Changed
  - Upgrade halpy to 18.0.0. (DO-230)

### [Lambda.P04] - 2018-02-19

-

- Changed
  - Upgrade halpy to 17.1.3. (DO-230)

### [Lambda.P03] - 2018-02-14

-

- Changed
  - Upgrade halpy to 17.1.2. (DO-202)
  - Upgraded Google Cloud SDK to 188.0.1.
  - Upgraded nuget to 4.5.1.

### [Lambda.P02] - 2018-02-01

-

- Changed
  - Upgrade halpy to 17.1.1. (DO-156)

### [Lambda.P01] - 2018-01-30

-

- Changed
  - Upgrade halpy to 17.1.0. (DO-143)

### [Lambda] - 2018-01-30

- Changed
  - Upgraded Python to 3.6.4. (DO-106)
  - Upgrade halpy to 17.0.0. (DO-137)
  - Upgraded Git to 2.16.1. (DO-137)
  - Upgraded Docker CE to 17.12. (DO-137)
  - Upgraded Google Cloud SDK to 186.0.0. (DO-137)
  - Upgraded MSBuild and MSTest to 2017 15.5.6. (DO-137)
  - Upgraded Node to 8.9.4. (DO-58)

### [Kappa.P03] - 2018-01-19

- Added
  - Added Google Cloud SDK support. (DO-102)

- Changed
  - Upgraded halpy to 16.1.0. (DO-103)

### [Kappa.P02] - 2018-01-11

- Changed
  - Upgraded halpy to 16.0.1. (DO-88)

### [Kappa.P01] - 2018-01-10

- Changed
  - Upgraded halpy to 16.0.0. (DO-83)
  - Updates to support updated halpy syscmd. (DO-79)

### [Kappa] - 2017-12-19

- Added
  - Added MSTest. (DO-48)

- Changed
  - Upgraded MSBuild to 2017 15.5.2. (DO-48)
  - Upgraded NuGet to 4.4.1. (DO-48)
  - Upgraded Node to 8.9.3. (DO-48)
  - Upgraded halpy to 15.4.0. (DO-46)

### [Iota.P08] - 2017-12-07

--

- Changed
  - Added MSBuild to the path. (DO-45)

### [Iota.P07] - 2017-12-07

--

- Changed
  - Upgraded halpy to 15.3.0. (DO-43)
  - Upgrade Windows Git to 2.15.1. (DO-43)

### [Iota.P06] - 2017-12-01

--

- Changed
  - Changed Docker container to use Alpine image.
  - Upgraded halpy to 15.2.0.

### [Iota.P05] - 2017-11-29

--

- Changed
  - Upgraded halpy to 15.1.1.

### [Iota.P04] - 2017-11-27

--

- Changed
  - Upgraded halpy to 15.0.5.

### [Iota.P03] - 2017-11-16

--

- Changed
  - Upgraded halpy to 15.0.3.

### [Iota.P02] - 2017-11-13

--

- Changed
  - Fixed update on Windows. (Bitbucket issue #17)
  - Upgraded Windows Git to 2.15.0.
  - Upgraded halpy to 15.0.1.

### [Iota.P01] - 2017-11-08

--

- Changed
  - Upgraded halpy to 14.0.4.

### [Iota] - 2017-11-06

- Added
  - Added support for building with Docker on Linux 3.10. (Bitbucket issue #10)
  - Added Visual Studio 2015 build tools including nuget. (Bitbucket issue #16)

  - Fix exception names to match new halpy.
  - Fix reverting of halpy on failed upgrade.
  - Upgraded Python to 3.6.3.
  - Upgraded halpy to 14.0.3.

### [Theta.P06] - 2017-10-03

- Changed
  - Fix uninstall of Git when upgraded on patch install.
  - Upgraded Node.js to 8.6.0.
  - Upgraded Windows Git to 2.14.2.
  - Upgraded halpy to 13.2.2.

### [Theta.P05] - 2017-09-28

- Changed
  - Upgraded halpy to 13.2.1.

### [Theta.P04] - 2017-09-26

- Changed
  - Upgraded halpy to 13.2.0.

### [Theta.P03] - 2017-09-25

- Changed
  - Upgraded halpy to 13.1.4.

### [Theta.P02] - 2017-09-21

- Changed
  - Upgraded halpy to 13.1.3.

### [Theta.P01] - 2017-09-21

- Changed
  - Upgraded Node.js to 8.5.0.
  - Upgraded halpy to 13.1.2.

### [Theta] - 2017-08-28

-

- Changed
  - Upgraded Python to 3.6.2.
  - Upgraded Node.js to 8.4.0.
  - Upgraded Windows Git to 2.14.1.
  - Upgraded halpy to 13.0.2.

### [Eta.P08] - 2017-08-24

-

- Changed
  - Updated build to use packages with versions. (Bitbucket issue #15)
  - Moved Linux Python build to separate product. (Bitbucket issue #14)
  - Upgraded halpy to 13.0.1.

### [Eta.P07] - 2017-08-22

-

- Changed
  - Upgraded halpy to 13.0.0.

### [Eta.P06] - 2017-08-18

-

- Changed
  - Upgraded halpy to 12.2.0.

### [Eta.P05] - 2017-08-17

-

- Changed
  - Upgraded halpy to 12.1.2.

### [Eta.P04] - 2017-08-14

-

- Changed
  - Upgraded halpy to 12.1.1.

### [Eta.P03] - 2017-08-11

-

- Changed
  - Upgraded halpy to 12.1.0.

### [Eta.P02] - 2017-08-08

-

- Changed
  - Upgraded halpy to 12.0.0.

### [Eta.P01] - 2017-07-12

-

- Changed
  - Upgraded halpy to 11.0.3.

### [Eta] - 2017-07-11

- Added
  - Git installation using yum for Linux installs.

- Changed
  - Upgraded Node to 8.1.3. (Bitbucket issue #11)
  - Fixed issue where halpy was still upgraded if overall upgrade failed. (Bitbucket issue #12)
  - Added Linux310x86_64 platform. (Bitbucket issue #13)
  - Improved bootstrap.

### [Zeta.P02] - 2017-07-06

--

- Changed
  - Upgraded halpy to 11.0.2.
  - Upgraded git on Windows to 2.13.2.

### [Zeta.P01] - 2017-06-21

--

- Changed
  - Upgraded halpy to 11.0.1.
  - Upgraded git on Windows to 2.13.1.2.

### [Zeta] - 2017-06-15

- Added
  - Added Linux support. (Bitbucket issue #7)
  - Add PSTool product. (Bitbucket issue #8)
  - Add sqlodbc product. (Bitbucket issue #9)
  - Add sqlcmd product. (Bitbucket issue #9)
  - Upgraded halpy to 10.0.3.
  - Upgraded Python to 3.6.1.
  - Add zip extract install method.
  - Fix issue with version search failing quietly.

### [Epsilon.P01] - 2017-06-01

--

- Changed
  - Upgraded halpy to 10.0.0.

### [Epsilon] - 2017-05-17

-
- Added
  - Git needed by gcv3 builds. (Bitbucket issue #4)

- Changed
  - Downgraded node.js to 6.1.0 to match what is run on the production servers. (Bitbucket issue #5)
  - Upgraded halpy to 9.0.0.
  - Renamed README.rst to README.md.
  - Fix issue with how <installargs> was applied.

### [Delta.P11] - 2017-06-01

- Changed
  - Upgraded halpy to 10.0.0.

### [Delta.P10] - 2017-04-26

- Changed
  - Upgraded halpy to 8.0.0.

### [Delta.P09] - 2017-04-24

- Changed
  - Upgraded halpy to 7.0.0.

### [Delta.P08] - 2017-04-21

- Changed
  - Upgraded halpy to 6.0.1.

### [Delta.P07] - 2017-04-17

- Changed
  - Upgraded halpy to 5.0.0.
  - Update source to meet Flake8 linting specs.

### [Delta.P06] - 2017-04-05

- Changed
  - Upgraded halpy to 4.4.0.

### [Delta.P05] - 2017-04-03

- Changed
  - Upgraded halpy to 4.3.1.

### [Delta.P04] - 2017-03-31

- Changed
  - Upgraded halpy to 4.3.0.

### [Delta.P03] - 2017-03-29

- Changed
  - Upgraded halpy to 4.2.0.
  - Use with statement for file access.

### [Delta.P02] - 2017-03-21

- Changed
  - Upgraded halpy to 4.1.1.

### [Delta.P01] - 2017-03-20

- Changed
  - Upgraded halpy to 4.1.0.

### [Delta] - 2017-03-17

- Added
  - Citrix NetScaler Python API.

- Changed
  - Upgraded halpy to 4.0.0.

### [Gamma.P06] - 2017-03-09

- Changed
  - Upgraded halpy to 3.0.0.

### [Gamma.P05] - 2017-03-07

- Changed
  - Upgraded halpy to 2.0.1.
  - Fixed output message on reinstall.

### [Gamma.P04] - 2017-03-06

- Changed
  - Updated renamed constant from halpy.
  - Upgraded halpy to 2.0.0.

- Removed
  - update command. Updates now handled by bart_install.ps1

### [Gamma.P03] - 2017-02-21

- Changed
  - Updated renamed constant from halpy.
  - Upgraded halpy to 1.0.0.

### [Gamma.P02] - 2017-02-09

- Changed
  - Provide method to pre-install halpy upgrade if changes are incompatible.  (Bitbucket issue #2)
  - Upgraded halpy to 0.12.

### [Gamma.P01] - 2017-02-09

- Changed
  - Upgraded halpy to 0.11.

### [Gamma] - 2017-02-07

- Changed
  - Upgraded halpy to 0.10.

- Removed
  - Packages that are now installed by halpy as requirements.

### [Beta.P01] - 2017-02-06

- Changed
  - Upgraded halpy to 0.9.

### [Beta] - 2017-02-06

- Changed
  - Updates to support updated halpy syscmd.
  - Rationalized imports.
  - Upgraded halpy to 0.8.
  - Updated setuptools to 34.1.1.

### [Alpha.P02] - 2017-01-27

- Changed
  - Updated halpy to 0.6.
  - Updated setuptools to 34.0.2.

### [Alpha.P01] - 2017-01-27

- Added
  - CHANGELOG.rst.
  - Send message to system to prevent need for reboot after install.

- Changed
  - Converted ReadMe.txt to README.rst.
  - Renamed doc directory to docs to follow new convention.
  - Fixed message in traceback on unknown sub-command.
  - Updated halpy ot 0.5.
  - Fixed issues with pip installs on update.

### [Alpha] - 2017-01-25

- Initial release

<!-- cSpell:ignore filecopy pywinrm pyparsing removeprefix removesuffix pylance sqldb ssdt servermgr versionlock syscmd sqlodbc sqlcmd installargs -->
<!-- cSpell:ignore sshpass sencha bumpver -->
