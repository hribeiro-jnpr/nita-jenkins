## ADDED Requirements

### Requirement: Plugin list declared in version control
The system SHALL maintain a `plugins.txt` file listing all required Jenkins plugins so the installed set is reproducible from source.

#### Scenario: Plugins installed at image build time
- **WHEN** the Docker image is built
- **THEN** every plugin named in `plugins.txt` is installed via `jenkins-plugin-cli`

### Requirement: Robot Framework plugin installed
The system SHALL include the `robot` plugin to display Robot Framework test results in the Jenkins UI.

#### Scenario: Robot results visible in Jenkins job view
- **WHEN** a job produces Robot Framework output and the `robot` plugin is installed
- **THEN** Jenkins renders a test results graph and pass/fail summary on the job page

### Requirement: AnsiColor plugin installed
The system SHALL include the `ansicolor` plugin to render ANSI colour codes in console output.

#### Scenario: Coloured console output in pipeline logs
- **WHEN** a pipeline step emits ANSI colour escape codes
- **THEN** the Jenkins console output renders colours instead of raw escape sequences

### Requirement: Plugin volume declared for caching
The system SHALL declare `/usr/share/jenkins/ref/plugins` as a Docker volume so plugin JPI files can be cached across container recreations.

#### Scenario: Plugin volume is mountable
- **WHEN** the container is started with a named volume for plugins
- **THEN** installed plugin JPI files persist on that volume
