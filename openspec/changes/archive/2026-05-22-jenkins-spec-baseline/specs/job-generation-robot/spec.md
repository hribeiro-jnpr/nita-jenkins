## ADDED Requirements

### Requirement: Job name and robot job name required
The system SHALL require the Ansible job name as the first argument and the Robot job name as a second argument, and exit non-zero if either is missing.

#### Scenario: Missing required arguments
- **WHEN** `robot.py` is called with fewer than two arguments
- **THEN** it prints a usage error and exits with a non-zero status code

### Requirement: Two calling conventions supported
The system SHALL accept either two arguments (job names only, images from environment) or four arguments (job names and explicit image names).

#### Scenario: Two-argument form uses environment variables for images
- **WHEN** `robot.py job_ansible job_robot` is called with `NITA_ANSIBLE_IMAGE` and `NITA_ROBOT_IMAGE` set
- **THEN** the generated manifests use those image values

#### Scenario: Four-argument form overrides images explicitly
- **WHEN** `robot.py job_ansible ansible_image job_robot robot_image` is called
- **THEN** the generated manifests use the explicitly provided image names

#### Scenario: Default images used when environment variables are unset
- **WHEN** two-argument form is used and neither `NITA_ANSIBLE_IMAGE` nor `NITA_ROBOT_IMAGE` is set
- **THEN** `ghcr.io/juniper/nita-ansible:latest` and `ghcr.io/juniper/nita-robot:latest` are used respectively

### Requirement: Two Kubernetes Job manifests written
The system SHALL produce two files: `<ansible-job-name>.yaml` and `<robot-job-name>.yaml` in the current working directory.

#### Scenario: Both output files created
- **WHEN** `robot.py` completes successfully
- **THEN** both `<ansible-job>.yaml` and `<robot-job>.yaml` exist in the current directory

### Requirement: Ansible job runs test_setup.sh
The system SHALL configure the Ansible job container to execute `bash test_setup.sh` inside the working directory.

#### Scenario: Ansible step runs setup script
- **WHEN** the Ansible Kubernetes Job runs
- **THEN** the container executes `bash test_setup.sh` in the project working directory

### Requirement: Robot job runs tests under test/ subdirectory
The system SHALL configure the Robot job container to run `robot -C ansi -L TRACE <path>/test/tests` and set `ROBOT_OPTIONS` to write outputs to `<path>/test/outputs`.

#### Scenario: Robot Framework executed in test subdirectory
- **WHEN** the Robot Kubernetes Job runs
- **THEN** the container's `workingDir` is set to `<project-path>/test` and `robot` is invoked against the `tests` directory

### Requirement: Shared volume from host project directory
Both generated jobs SHALL mount `/var/nita_project` at `/project/` so Ansible setup results are visible to the Robot test step.

#### Scenario: Robot job can read Ansible outputs
- **WHEN** the Ansible job writes files under `/project/`
- **THEN** the Robot job container can read those files from the same mounted path

### Requirement: Jobs use NITA namespace
Both generated manifests SHALL target `metadata.namespace: nita`.

#### Scenario: Jobs deploy to nita namespace
- **WHEN** manifests are applied with `kubectl apply`
- **THEN** both Jobs are created in the `nita` namespace

### Requirement: No retry, automatic cleanup
Both jobs SHALL set `backoffLimit: 0` and `ttlSecondsAfterFinished: 120`.

#### Scenario: Failed jobs do not retry and are cleaned up
- **WHEN** either job pod exits with non-zero
- **THEN** Kubernetes does not reschedule it, and after 120 seconds the Job object is deleted
