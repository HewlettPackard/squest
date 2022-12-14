# Release new version of Squest

## Prepare

- Create a `release` branch
- Update the `CHANGELOG.md`
- Delete all migration file since the last release in all Django app
- Make migration files
- Update `Squest/version.py` with release version
- Update version in Poetry `pyproject.toml`
- PR --> master
- Last review and rebase/merge master

## CI execution

From here the CI will:

- Build the new docker image
- Push the image in [quay.io](https://quay.io/repository/hewlettpackardenterprise/squest)
- Build and publish the mkdocs documentation into [GitHub pages](https://hewlettpackard.github.io/squest/latest/)


## Post CI

- Tag the branch with the new version and push the tag
- Create a release from the pushed tag on GitHub
- Create new dev branch
  - Update `version.py` with new beta version
  - Update poetry version in `pyproject.toml` with new beta version (E.g: `1.8.3b`)
  - Bump poetry libraries
  - Force push the new dev branch to upstream
- Notify community in [Gitter](https://gitter.im/HewlettPackard/squest)
