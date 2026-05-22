## ADDED Requirements

### Requirement: HTTPS port exposure
The system SHALL expose Jenkins on host port 8443 mapped to container port 8443.

#### Scenario: Jenkins reachable from host browser
- **WHEN** the container is running
- **THEN** `https://localhost:8443` returns the Jenkins UI

### Requirement: Docker socket bind-mount
The system SHALL mount the host Docker socket (`/var/run/docker.sock`) into the container so Jenkins jobs can launch sibling containers.

#### Scenario: Jenkins pipeline can run Docker commands
- **WHEN** a pipeline step executes `docker run`
- **THEN** the command uses the host Docker daemon

### Requirement: Docker binary bind-mount read-only
The system SHALL mount the host `docker` binary at `/usr/bin/docker` as read-only.

#### Scenario: Docker CLI available inside container without installing Docker
- **WHEN** a pipeline step calls `docker`
- **THEN** the host binary is used and the container does not need Docker installed separately

### Requirement: Project directory mount
The system SHALL mount `/var/nita_project` from the host at `/project` inside the container with read-write access.

#### Scenario: Pipeline reads and writes project files
- **WHEN** a Jenkins job writes output to `/project/`
- **THEN** files appear under `/var/nita_project/` on the host

### Requirement: Jenkins home persistent volume
The system SHALL use a named Docker volume `jenkins_home` for `/var/jenkins_home` to persist Jenkins state across container recreations.

#### Scenario: Jobs survive image upgrade
- **WHEN** the container is recreated with a new image version
- **THEN** existing Jenkins jobs and configuration are present

### Requirement: TLS keystore mount
The system SHALL mount a JKS keystore from `./certificates/jenkins_keystore.jks` into the container at `/var/jenkins_home/jenkins_keystore.jks`.

#### Scenario: Jenkins serves valid HTTPS
- **WHEN** the container starts with a valid keystore file present
- **THEN** Jenkins accepts TLS connections using that certificate

### Requirement: HTTPS configured via environment variable
The system SHALL configure Jenkins HTTPS via `JENKINS_OPTS` using the mounted keystore, password `nita123`, on port 8443, with HTTP on port 8080.

#### Scenario: Jenkins starts with HTTPS enabled
- **WHEN** the container starts
- **THEN** `JENKINS_OPTS` is set to `--httpPort=8080 --httpsPort=8443 --httpsKeyStore=... --httpsKeyStorePassword=nita123`

### Requirement: NITA network membership
The system SHALL attach the Jenkins container to the pre-existing external Docker network `nita-network`.

#### Scenario: Jenkins can reach other NITA containers by hostname
- **WHEN** another NITA service is on `nita-network`
- **THEN** Jenkins can reach it by its service hostname

### Requirement: Automatic restart policy
The system SHALL set `restart: always` so Jenkins restarts automatically after host reboots or container crashes.

#### Scenario: Jenkins restarts after host reboot
- **WHEN** the host reboots with Docker set to start on boot
- **THEN** the Jenkins container starts automatically
