## ADDED Requirements

### Requirement: Input read from data.json
The system SHALL read a `data.json` file from the current working directory containing a JSON object whose keys are relative file paths and whose values are YAML-serialisable objects.

#### Scenario: Valid data.json processed successfully
- **WHEN** `write_yaml_files.py` is executed and `data.json` exists and is valid JSON
- **THEN** the script processes each key-value pair without error

#### Scenario: Missing data.json
- **WHEN** `write_yaml_files.py` is executed and `data.json` does not exist
- **THEN** the script prints an error message and exits without creating any files

### Requirement: Only group_vars and host_vars paths accepted
The system SHALL only write output files whose path contains `group_vars/` or `host_vars/` AND ends in `.yaml` or `.yml`. All other keys SHALL be logged as invalid and skipped.

#### Scenario: Valid group_vars path written
- **WHEN** a key is `group_vars/all/main.yaml`
- **THEN** the file is created at that relative path with YAML content

#### Scenario: Invalid path skipped with warning
- **WHEN** a key is `config/settings.yaml` (no `group_vars/` or `host_vars/`)
- **THEN** the script prints `"Invalid File Name Found ====> config/settings.yaml"` and does not create the file

### Requirement: Output written as YAML with explicit document start
The system SHALL write each output file using `yaml.safe_dump` with `explicit_start=True`, producing a document-start marker (`---`).

#### Scenario: Output file starts with YAML document marker
- **WHEN** a YAML file is written
- **THEN** the first line of the file is `---`

### Requirement: Null values represented as empty strings
The system SHALL register a custom YAML representer so Python `None` values are serialised as an empty YAML scalar (not `null`).

#### Scenario: None values produce empty YAML values
- **WHEN** the input JSON contains `null` values
- **THEN** the written YAML shows an empty value, not the string `null`

### Requirement: Output directories created on demand
The system SHALL create any missing intermediate directories before writing each output file.

#### Scenario: Nested path created automatically
- **WHEN** a key path includes subdirectories that do not yet exist
- **THEN** `os.makedirs` creates them before writing the file

### Requirement: Output files set world-readable-writable-executable
The system SHALL set permissions `0o775` on each written file.

#### Scenario: Written files are group-writable
- **WHEN** a YAML file is written
- **THEN** its Unix permissions are `rwxrwxr-x` (0o775)
