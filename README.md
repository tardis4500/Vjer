# Build and Release Toolkit Images

This repository provides support images for build and deploy activities.

## Testing

The following should be tested before a new BaRT release.

- All changes
  - [SRECleaner](https://gitlab.buildone.co/cc/sre/srecleaner)
  - [SRECleanerDeployer](https://gitlab.buildone.co/deployers/srecleanerdeployer)
- Linux changes
  - [ExportAgent](https://gitlab.buildone.co/product-development/cc-platform/export)
  - [PPR UI](https://gitlab.buildone.co/product-development/cc-platform/ppr)
  - [AdminPortal BE](https://gitlab.buildone.co/product-development/cc-platform/admin-portal/ccs.adminportal)
  - [AdminPortal UI](https://gitlab.buildone.co/product-development/cc-platform/admin-portal/adminportal-frontend)
  - [UI Component Library](https://gitlab.buildone.co/product-development/cc-platform/ui-component-library)
  - [Entitlements](https://gitlab.buildone.co/product-development/cc-platform/CCS.Entitlements)
- Windows changes
  - [PPR BE](https://gitlab.buildone.co/product-development/cc-platform/project-plan-room)

The test procedure is performed from the util directory

1. Test the SRECleaner build and deploy:
    - python test_images.py {BaRT-Template-Branch} SRECleaner
    - run the deploy-development job
    - run the pre-release job
    - remove the test branch
1. Test the SRECleanerDeployer deployments:
    - python test_images.py {BaRT-Template-Branch} SRECleanerDeployer {SRECleaner-Pre-Release-Version}
    - create a new pipeline for the SRECleanerDeployer on the release/bart-testing branch
    - run the deploy-staging job
    - remove the test branch
1. For each of the remaining projects
    - python test_images.py {BaRT-Template-Branch} {Project}
    - run any manual scans
    - remove the test branch
    - remove the test pipeline

<!-- cSpell:ignore cicd -->
