## ADDED Requirements

### Requirement: Backup destination directory required
The system SHALL require a destination directory path as the first argument to `backup-jenkins.sh` and exit non-zero if it is absent.

#### Scenario: Missing destination argument
- **WHEN** `backup-jenkins.sh` is called with no arguments
- **THEN** it prints an error and exits with a non-zero status

### Requirement: Backup script copied and executed inside the container
The system SHALL copy `backup-jenkins-in.sh` into the Jenkins container, set ownership to `jenkins:jenkins`, and execute it as the `jenkins` user.

#### Scenario: In-container backup script runs with correct permissions
- **WHEN** `backup-jenkins.sh` is called with a destination path
- **THEN** `backup-jenkins-in.sh` is copied to `/var/jenkins_home/` and executed inside the container

### Requirement: Configuration, jobs, nodes, secrets, and users backed up
The system SHALL back up Jenkins XML configuration files at `/var/jenkins_home/*.xml`, job definitions at `/var/jenkins_home/jobs/**/*.xml`, nodes, secrets, and user records into a tar archive.

#### Scenario: Backup archive contains Jenkins configuration
- **WHEN** the backup completes
- **THEN** the tar archive contains Jenkins global config, all job XML files, and user account data

### Requirement: Plugin list and plugin JPI files backed up separately
The system SHALL produce a separate plugin tar archive containing all installed `.jpi` files and a text list of installed plugin versions.

#### Scenario: Plugin backup archive produced
- **WHEN** the backup completes
- **THEN** a `jenkins_plugins_backup.tar` archive exists containing all `.jpi` files

### Requirement: Backup archive transferred to host destination directory
The system SHALL copy both archives from the container to the host path supplied as the first argument.

#### Scenario: Archives available on host after backup
- **WHEN** the backup script completes
- **THEN** `jenkins_backup.tar` and `jenkins_plugins_backup.tar` are present in the destination directory

### Requirement: Restore archive path required
The system SHALL require the path to a backup archive as the first argument to `restore-jenkins.sh` and exit non-zero if it is absent.

#### Scenario: Missing archive argument
- **WHEN** `restore-jenkins.sh` is called with no arguments
- **THEN** it prints an error and exits with a non-zero status

### Requirement: Archive extracted and restored into container
The system SHALL extract the supplied archive to a temporary directory and then copy the contents back into the Jenkins container, preserving permissions.

#### Scenario: Jenkins configuration restored from archive
- **WHEN** `restore-jenkins.sh` is called with a valid backup archive path
- **THEN** Jenkins XML files and plugin archives are restored to `/var/jenkins_home/` inside the container

### Requirement: CLI backup command delegates to backup script
The `nita-cmd_jenkins_backup` CLI script SHALL resolve the backup script directory from `NITAJENKINSDIR` (defaulting to `/etc/nita-jenkins/backup`) and invoke `backup-jenkins.sh` with the supplied argument.

#### Scenario: CLI backup command invokes backup-jenkins.sh
- **WHEN** `nita-cmd_jenkins_backup /tmp/backup-output` is called
- **THEN** `backup-jenkins.sh /tmp/backup-output` is executed from the correct directory

### Requirement: CLI restore command resolves absolute path before delegating
The `nita-cmd_jenkins_restore` CLI script SHALL resolve the supplied archive path to an absolute path before invoking `restore-jenkins.sh`.

#### Scenario: Relative archive path resolved correctly
- **WHEN** `nita-cmd_jenkins_restore ../backup.tar` is called from a subdirectory
- **THEN** `restore-jenkins.sh` receives the absolute path to `backup.tar`
