## ADDED Requirements

### Requirement: Base image
The system SHALL use `jenkins/jenkins:lts-jdk17` as the base Docker image.

#### Scenario: Base image is LTS with JDK 17
- **WHEN** the Docker image is built
- **THEN** it is derived from the official Jenkins LTS image with JDK 17

### Requirement: Setup wizard disabled
The system SHALL disable the Jenkins setup wizard on first boot.

#### Scenario: No interactive setup on first start
- **WHEN** the container starts for the first time
- **THEN** Jenkins proceeds directly to the main UI without prompting for initial configuration

### Requirement: CSP header relaxed for same-origin
The system SHALL set the Content-Security-Policy to `allow-same-origin` to support embedded build reports.

#### Scenario: Same-origin resources load in build views
- **WHEN** a build page embeds a report from the same origin
- **THEN** the browser does not block the content due to CSP

### Requirement: Architecture-aware kubectl installation
The system SHALL install `kubectl` matching the stable release, selecting the binary for the host CPU architecture (`amd64` or `arm64`).

#### Scenario: Build on amd64 host
- **WHEN** `KUBECTL_ARCH` build arg is `amd64`
- **THEN** the amd64 `kubectl` binary is placed at `/usr/local/bin/kubectl`

#### Scenario: Build on arm64 host
- **WHEN** `KUBECTL_ARCH` build arg is `arm64`
- **THEN** the arm64 `kubectl` binary is placed at `/usr/local/bin/kubectl`

### Requirement: System packages installed
The system SHALL install the following OS packages: `git-core`, `curl`, `libssl-dev`, `build-essential`, `libffi-dev`, `python3-dev`, `python3-yaml`, `python3-pip`, `sshpass`, `apache2-suexec-custom`, `wget`, `vim`.

#### Scenario: Required binaries available inside container
- **WHEN** a Jenkins job runs inside the container
- **THEN** `git`, `curl`, `python3`, `pip3`, and `sshpass` are available on `PATH`

### Requirement: Python scripts deployed to PATH
The system SHALL copy `write_yaml_files.py`, `robot.py`, and `create_ansible_job_k8s.py` to `/usr/local/bin` and make them executable.

#### Scenario: Scripts callable from Jenkins pipeline
- **WHEN** a Jenkins pipeline step calls `write_yaml_files.py` without a path prefix
- **THEN** the script is found and executed

### Requirement: Image version tag sourced from VERSION.txt
The system SHALL be tagged using the version string from `VERSION.txt` when built via `build_container.sh`.

#### Scenario: Reproducible image tag
- **WHEN** `build_container.sh` is executed
- **THEN** the resulting image is tagged `juniper/nita-jenkins:<version>` where `<version>` is the trimmed content of `VERSION.txt`

### Requirement: Jenkins volumes declared
The system SHALL declare two volumes: `/usr/share/jenkins/ref/plugins` and `/var/jenkins_home`.

#### Scenario: Persistent state survives container restart
- **WHEN** a container is stopped and a new one started with the same named volume
- **THEN** Jenkins jobs, configuration, and installed plugins are preserved

### Requirement: Health check on HTTPS
The system SHALL include a Docker `HEALTHCHECK` that performs an HTTPS request to `localhost:8443` and exits non-zero if the response is not received.

#### Scenario: Container reports healthy when Jenkins is up
- **WHEN** Jenkins is fully started and serving HTTPS
- **THEN** `docker inspect` reports the container status as `healthy`
