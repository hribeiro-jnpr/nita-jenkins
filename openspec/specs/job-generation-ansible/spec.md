# Job Generation (Ansible) Specification

## Purpose
Defines the behaviour of `create_ansible_job_k8s.py`, which generates a Kubernetes
Job manifest for running an Ansible step within the NITA pipeline.

## Requirements

### Requirement: Job name required
The system SHALL require a job name as the first positional argument and exit non-zero if it is absent.

#### Scenario: Missing job name argument
- GIVEN `create_ansible_job_k8s.py` is called with no arguments
- WHEN the script runs
- THEN it prints a usage error and exits with a non-zero status code

### Requirement: Ansible image configurable via argument or environment
The system SHALL accept the Ansible container image as the second positional argument; if absent, it SHALL fall back to the `NITA_ANSIBLE_IMAGE` environment variable, defaulting to `ghcr.io/juniper/nita-ansible:latest`.

#### Scenario: Image override via argument
- GIVEN `create_ansible_job_k8s.py myjob mycustom/image:1.0` is called
- WHEN the script runs
- THEN the generated manifest uses `mycustom/image:1.0` as the container image

#### Scenario: Image from environment variable
- GIVEN `NITA_ANSIBLE_IMAGE=my/ansible:2.0` is set and no image argument is given
- WHEN the script runs
- THEN the generated manifest uses `my/ansible:2.0`

#### Scenario: Default image used when no override provided
- GIVEN no image argument is given and `NITA_ANSIBLE_IMAGE` is unset
- WHEN the script runs
- THEN the generated manifest uses `ghcr.io/juniper/nita-ansible:latest`

### Requirement: Kubernetes Job manifest written to file
The system SHALL write a valid Kubernetes `batch/v1 Job` manifest to `<job-name>.yaml` in the current working directory.

#### Scenario: Output file created
- GIVEN `create_ansible_job_k8s.py myjob` is called
- WHEN the script completes
- THEN `myjob.yaml` is created containing a well-formed Kubernetes Job spec

### Requirement: Job targets NITA namespace
The system SHALL set `metadata.namespace: nita` in the generated manifest.

#### Scenario: Job deployed to nita namespace
- GIVEN the manifest is applied with `kubectl apply`
- WHEN Kubernetes processes it
- THEN the Job is created in the `nita` namespace

### Requirement: Working directory set to current path
The system SHALL set `workingDir` in the container spec to the current working directory of the calling process at generation time.

#### Scenario: Ansible runs in the project directory
- GIVEN `create_ansible_job_k8s.py` is called from `/var/nita_project/myproject`
- WHEN the manifest is generated
- THEN the container's `workingDir` is `/var/nita_project/myproject`

### Requirement: Job entrypoint runs named shell script
The system SHALL configure the container to execute `/bin/bash -c "bash <job-name>.sh"`.

#### Scenario: Job runs the project shell script
- GIVEN the generated Job is submitted to Kubernetes
- WHEN the container starts
- THEN it executes `bash <job-name>.sh` inside the working directory

### Requirement: Project volume mounted from host path
The system SHALL mount `/var/nita_project` (type `DirectoryOrCreate`) at `/project/` inside the container.

#### Scenario: Ansible job can read project files
- GIVEN the Kubernetes Job runs
- WHEN the container accesses `/project/`
- THEN files under `/var/nita_project/` on the node are accessible

### Requirement: No retry on failure
The system SHALL set `backoffLimit: 0` so a failed job is not retried automatically.

#### Scenario: Failed job does not retry
- GIVEN the container exits with a non-zero status
- WHEN Kubernetes evaluates the Job
- THEN it marks the Job as failed and does not reschedule the pod

### Requirement: Job cleaned up after completion
The system SHALL set `ttlSecondsAfterFinished: 120` so completed Job objects are garbage-collected after two minutes.

#### Scenario: Completed job is removed
- GIVEN the Job finishes (success or failure)
- WHEN 120 seconds elapse
- THEN Kubernetes deletes the Job and its pod
