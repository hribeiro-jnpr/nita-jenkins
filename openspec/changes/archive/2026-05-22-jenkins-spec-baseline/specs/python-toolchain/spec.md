## ADDED Requirements

### Requirement: Python dependencies declared in requirements.txt
The system SHALL maintain a `requirements.txt` file listing all Python packages required by pipeline scripts so dependencies are reproducible.

#### Scenario: Packages installed into image
- **WHEN** the Docker image is built
- **THEN** every package in `requirements.txt` is installed via `pip3 install --break-system-packages`

### Requirement: Network automation libraries available
The system SHALL install `ansible`, `ncclient`, `junos-eznc`, `python-jenkins`, and `jenkinsapi` so Jenkins pipeline scripts can drive network device automation.

#### Scenario: Ansible playbook can be invoked from pipeline
- **WHEN** a pipeline step calls `ansible-playbook`
- **THEN** Ansible is found on `PATH` and executes without missing-module errors

### Requirement: Cloud and OpenStack clients available
The system SHALL install `python-openstackclient`, `shade`, and `python-novaclient` to support OpenStack-based lab provisioning jobs.

#### Scenario: OpenStack CLI available in pipeline
- **WHEN** a pipeline step calls `openstack`
- **THEN** the command is found and authenticated against an OpenStack endpoint

### Requirement: YAML and Jinja2 libraries available
The system SHALL install `PyYAML` and `Jinja2` so pipeline scripts can read/write YAML files and render templates.

#### Scenario: write_yaml_files.py runs without import errors
- **WHEN** `write_yaml_files.py` is executed inside the container
- **THEN** `import yaml` and `import json` succeed

### Requirement: Linting tools available
The system SHALL install `ansible-lint` and `pylint` so pipeline stages can perform static analysis.

#### Scenario: ansible-lint executable on PATH
- **WHEN** a pipeline step calls `ansible-lint`
- **THEN** the tool executes and returns a lint report
