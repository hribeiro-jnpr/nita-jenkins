# YAML File Writer Specification

## Purpose
Defines the behaviour of `write_yaml_files.py`, which reads a `data.json` file
from the working directory and writes Ansible group_vars/host_vars YAML files.

## Requirements

### Requirement: Input read from data.json
The system SHALL read a `data.json` file from the current working directory containing a JSON object whose keys are relative file paths and whose values are YAML-serialisable objects.

#### Scenario: Valid data.json processed successfully
- GIVEN `data.json` exists and is valid JSON
- WHEN `write_yaml_files.py` is executed
- THEN the script processes each key-value pair without error

#### Scenario: Missing data.json
- GIVEN `data.json` does not exist in the current directory
- WHEN `write_yaml_files.py` is executed
- THEN the script prints an error message and exits without creating any files

### Requirement: Only group_vars and host_vars paths accepted
The system SHALL only write output files whose path contains `group_vars/` or `host_vars/` AND ends in `.yaml` or `.yml`. All other keys SHALL be logged as invalid and skipped.

#### Scenario: Valid group_vars path written
- GIVEN a key is `group_vars/all/main.yaml`
- WHEN the script processes it
- THEN the file is created at that relative path with YAML content

#### Scenario: Invalid path skipped with warning
- GIVEN a key is `config/settings.yaml` (no `group_vars/` or `host_vars/` prefix)
- WHEN the script processes it
- THEN it prints `Invalid File Name Found ====> config/settings.yaml` and does not create the file

### Requirement: Output written as YAML with explicit document start
The system SHALL write each output file using `yaml.safe_dump` with `explicit_start=True`, producing a document-start marker (`---`).

#### Scenario: Output file starts with YAML document marker
- GIVEN a valid path is processed
- WHEN the YAML file is written
- THEN the first line of the file is `---`

### Requirement: Null values represented as empty strings
The system SHALL register a custom YAML representer so Python `None` values are serialised as an empty YAML scalar (not `null`).

#### Scenario: None values produce empty YAML values
- GIVEN the input JSON contains `null` values
- WHEN the YAML file is written
- THEN the output shows an empty value rather than the string `null`

### Requirement: Output directories created on demand
The system SHALL create any missing intermediate directories before writing each output file.

#### Scenario: Nested path created automatically
- GIVEN a key path includes subdirectories that do not yet exist
- WHEN the file is written
- THEN the intermediate directories are created before writing

### Requirement: Output files set world-readable-writable-executable
The system SHALL set permissions `0o775` on each written file.

#### Scenario: Written files are group-writable
- GIVEN a YAML file has been written
- WHEN the file permissions are inspected
- THEN they are `rwxrwxr-x` (0o775)
