# Jenkins Security Specification

## Purpose
Defines how the Jenkins admin account is bootstrapped at startup and what
authorisation strategy is applied, using environment-variable-supplied credentials.

## Requirements

### Requirement: Admin user created from environment variables
The system SHALL create a Jenkins admin account using credentials read from `JENKINS_USER` and `JENKINS_PASS` environment variables at first boot.

#### Scenario: Fresh container with no existing users
- GIVEN Jenkins starts with an empty `jenkins_home` volume
- WHEN the init Groovy script runs
- THEN an admin account is created with the username and password from `JENKINS_USER` and `JENKINS_PASS`

### Requirement: Existing admin password update
The system SHALL update the admin user's password if the account already exists, without creating a duplicate account.

#### Scenario: Container restart with pre-existing admin
- GIVEN Jenkins starts and the admin user already exists in the security realm
- WHEN the init script runs
- THEN the password is updated to the current value of `JENKINS_PASS` and no duplicate account is created

### Requirement: Full-control-once-logged-in authorisation
The system SHALL configure `FullControlOnceLoggedInAuthorizationStrategy` so that any authenticated user has full Jenkins access.

#### Scenario: Logged-in user can perform all operations
- GIVEN a user has authenticated successfully
- WHEN they attempt to create, run, or delete a job
- THEN the action is permitted without additional role assignment

### Requirement: Security bootstrapped via init script
The system SHALL apply security configuration at startup via a Groovy init script placed in `/var/jenkins_home/init.groovy.d/`.

#### Scenario: Security is active before any user interaction
- GIVEN Jenkins completes its startup sequence
- WHEN the first HTTP request arrives
- THEN the security realm and authorisation strategy are already configured
