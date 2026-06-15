## 1. Publish container-image spec

- [x] 1.1 Copy `openspec/changes/jenkins-spec-baseline/specs/container-image/spec.md` to `openspec/specs/container-image/spec.md`
- [x] 1.2 Verify spec covers base image, setup wizard, CSP header, kubectl arch, system packages, Python scripts on PATH, version tag, volumes, and health check

## 2. Publish container-runtime spec

- [x] 2.1 Copy `openspec/changes/jenkins-spec-baseline/specs/container-runtime/spec.md` to `openspec/specs/container-runtime/spec.md`
- [x] 2.2 Verify spec covers HTTPS port, Docker socket, docker binary mount, project directory mount, persistent volume, TLS keystore, JENKINS_OPTS, network, and restart policy

## 3. Publish jenkins-security spec

- [x] 3.1 Copy `openspec/changes/jenkins-spec-baseline/specs/jenkins-security/spec.md` to `openspec/specs/jenkins-security/spec.md`
- [x] 3.2 Verify spec covers admin creation from env vars, password update, full-control authorisation, and init-script bootstrap

## 4. Publish jenkins-plugins spec

- [x] 4.1 Copy `openspec/changes/jenkins-spec-baseline/specs/jenkins-plugins/spec.md` to `openspec/specs/jenkins-plugins/spec.md`
- [x] 4.2 Verify spec covers plugins.txt reproducibility, robot plugin, ansicolor plugin, and plugin volume

## 5. Publish python-toolchain spec

- [x] 5.1 Copy `openspec/changes/jenkins-spec-baseline/specs/python-toolchain/spec.md` to `openspec/specs/python-toolchain/spec.md`
- [x] 5.2 Verify spec covers requirements.txt reproducibility, network automation libs, cloud clients, YAML/Jinja2, and linting tools

## 6. Publish job-generation-ansible spec

- [x] 6.1 Copy `openspec/changes/jenkins-spec-baseline/specs/job-generation-ansible/spec.md` to `openspec/specs/job-generation-ansible/spec.md`
- [x] 6.2 Verify spec covers required arguments, image selection precedence, output file format, namespace, working dir, entrypoint, volume mount, backoffLimit, and TTL

## 7. Publish job-generation-robot spec

- [x] 7.1 Copy `openspec/changes/jenkins-spec-baseline/specs/job-generation-robot/spec.md` to `openspec/specs/job-generation-robot/spec.md`
- [x] 7.2 Verify spec covers two calling conventions, two output files, ansible entrypoint, robot test path, shared volume, namespace, and retry/cleanup settings

## 8. Publish yaml-file-writer spec

- [x] 8.1 Copy `openspec/changes/jenkins-spec-baseline/specs/yaml-file-writer/spec.md` to `openspec/specs/yaml-file-writer/spec.md`
- [x] 8.2 Verify spec covers data.json input, path validation, YAML output format, null representer, directory creation, and file permissions

## 9. Publish backup-restore spec

- [x] 9.1 Copy `openspec/changes/jenkins-spec-baseline/specs/backup-restore/spec.md` to `openspec/specs/backup-restore/spec.md`
- [x] 9.2 Verify spec covers backup destination requirement, in-container script execution, configuration/jobs/secrets/users backup, plugin archive, host transfer, restore argument, archive extraction, CLI delegation, and absolute path resolution

## 10. Publish cli-commands spec

- [x] 10.1 Copy `openspec/changes/jenkins-spec-baseline/specs/cli-commands/spec.md` to `openspec/specs/cli-commands/spec.md`
- [x] 10.2 Verify spec covers runtime dispatch (kubectl vs docker), lifecycle commands (up/down/start/stop/restart), job management (create/delete/enable/disable/ls/get), CLI access, informational commands, plugin introspection, SSL toggle, debug mode, NITAJENKINSDIR override, and help file co-location

## 11. Validate all specs

- [x] 11.1 Run `openspec validate jenkins-spec-baseline` and confirm no errors
- [x] 11.2 Confirm `openspec list --specs` shows all 10 capability specs after archive
