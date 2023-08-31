# Release Notes

Squest releases are numbered as major, minor, and patch releases. 
For example, version `1.1.0` is a minor release, and `1.1.5` is a patch release. These can be described as follows:

- **Major** - Introduces or removes an entire API or other core functionality
- **Minor** - Implements major new features but may include breaking changes for API consumers or other integrations
- **Patch** - A maintenance release which fixes bugs and may introduce backward-compatible enhancements

## v2.0.0

This is a **major** update of Squest:

- The resource tracker component has been entirely refactored and cannot be migrated automatically
- The API has been reworked

To migrate from v1 to v2 if you were using the **resource tracking** feature:

- Make sure that _attribute definitions_ that are common (same type) are exactly the same **name**
- Follow the [upgrade documentation](administration/upgrade.md) to bump your current Squest installation to the last v1 version available: `v1.10.5`
- Execute the resource tracker export script:

```bash
docker-compose exec -T django python3 manage.py export_resource_tracker_v1
```

- Follow the upgrade documentation to bump your installation to `v2.X.X`
- Execute the resource tracker import script: 

```bash
docker-compose exec -T django python3 manage.py import_resource_tracker_v1
```
