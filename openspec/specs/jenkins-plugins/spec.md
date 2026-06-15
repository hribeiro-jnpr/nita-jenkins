# Jenkins Plugins Specification

## Purpose
Defines the Jenkins plugin set required by nita-jenkins, how plugins are installed
at image build time, and the volume used to cache them.

## Requirements

### Requirement: Plugin list declared in version control
The system SHALL maintain a `plugins.txt` file listing all required Jenkins plugins so the installed set is reproducible from source.

#### Scenario: Plugins installed at image build time
- GIVEN `plugins.txt` lists the required plugins
- WHEN the Docker image is built
- THEN every plugin named in `plugins.txt` is installed via `jenkins-plugin-cli`

### Requirement: Robot Framework plugin installed
The system SHALL include the `robot` plugin to display Robot Framework test results in the Jenkins UI.

#### Scenario: Robot results visible in Jenkins job view
- GIVEN the `robot` plugin is installed
- WHEN a job produces Robot Framework output
- THEN Jenkins renders a test results graph and pass/fail summary on the job page

### Requirement: AnsiColor plugin installed
The system SHALL include the `ansicolor` plugin to render ANSI colour codes in console output.

#### Scenario: Coloured console output in pipeline logs
- GIVEN the `ansicolor` plugin is installed
- WHEN a pipeline step emits ANSI colour escape codes
- THEN the Jenkins console output renders colours instead of raw escape sequences

### Requirement: Plugin volume declared for caching
The system SHALL declare `/usr/share/jenkins/ref/plugins` as a Docker volume so plugin JPI files can be cached across container recreations.

#### Scenario: Plugin volume is mountable
- GIVEN a named volume is mounted at `/usr/share/jenkins/ref/plugins`
- WHEN the container is started
- THEN installed plugin JPI files persist on that volume
