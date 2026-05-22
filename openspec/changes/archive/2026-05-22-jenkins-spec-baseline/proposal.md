## Why

The nita-jenkins codebase has no formal specifications, making it hard to reason about intended behaviour before making changes. Capturing the current system as machine-readable specs creates a safety net so future changes can be validated against known requirements without accidentally breaking existing functionality.

## What Changes

- Introduce `openspec/specs/` hierarchy with one spec file per capability area
- No runtime code is modified — this is a documentation-only change that establishes a spec baseline

## Capabilities

### New Capabilities

- `container-image`: Docker image definition, base image selection, installed toolchain, and build process via `build_container.sh`
- `container-runtime`: Docker Compose service configuration, port mapping, volume mounts, networking, and environment variables
- `jenkins-security`: Initial admin account bootstrap via `basic-security.groovy`, credentials sourced from environment variables
- `jenkins-plugins`: Plugin set declared in `plugins.txt` and installed at image-build time via `jenkins-plugin-cli`
- `python-toolchain`: Python 3 dependencies in `requirements.txt` installed into the image; scripts available on `PATH`
- `job-generation-ansible`: `create_ansible_job_k8s.py` — generates a Kubernetes `Job` manifest for running an Ansible step in the NITA pipeline
- `job-generation-robot`: `robot.py` — generates paired Kubernetes `Job` manifests for Ansible + Robot Framework test steps
- `yaml-file-writer`: `write_yaml_files.py` — reads `data.json` from the workspace and writes Ansible `group_vars`/`host_vars` YAML files
- `backup-restore`: `backup_script/` — backup and restore of Jenkins configuration, jobs, users, secrets, and plugins to/from a tar archive
- `cli-commands`: `cli_scripts/` — shell wrappers (`nita-cmd_jenkins_*`) that dispatch Jenkins operations to either `kubectl` or `docker-compose` depending on available runtime

### Modified Capabilities

<!-- None — this is a greenfield spec capture with no existing specs to modify -->

## Impact

- Adds `openspec/specs/` directory tree (documentation only, not deployed)
- No changes to `Dockerfile`, scripts, or runtime configuration
- Provides the spec foundation required before any future functional change can be proposed
