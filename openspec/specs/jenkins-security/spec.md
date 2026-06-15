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
The system SHALL detect whether the admin account already exists by comparing against the `JENKINS_USER` environment variable, updating the password if found, and creating the account only if it does not yet exist.

#### Scenario: Container restart with pre-existing admin
- GIVEN Jenkins starts and the admin user (from `JENKINS_USER`) already exists in the security realm
- WHEN the init script runs
- THEN the password is updated to the current value of `JENKINS_PASS` and no duplicate account is created

#### Scenario: First boot creates admin account
- GIVEN Jenkins starts with an empty `jenkins_home` volume
- WHEN the init script runs
- THEN an admin account is created with credentials from `JENKINS_USER` and `JENKINS_PASS`

### Requirement: Full-control-once-logged-in authorisation
The system SHALL configure `GlobalMatrixAuthorizationStrategy` granting authenticated users full access and granting anonymous users `Job/Build`, `Job/Read`, and `Job/Cancel` permissions only.

#### Scenario: Authenticated user has full access
- GIVEN a user has authenticated successfully
- WHEN they attempt to create, run, configure, or delete a job
- THEN the action is permitted

#### Scenario: Anonymous user can trigger, read, and cancel jobs
- GIVEN no authentication credentials are provided
- WHEN an HTTP request to trigger, read status, or cancel a job is made on port 8080
- THEN the request is permitted (HTTP 200 / 201)

#### Scenario: Anonymous user cannot access admin functions
- GIVEN no authentication credentials are provided
- WHEN an HTTP request to configure Jenkins, manage credentials, or access system settings is made
- THEN the request is rejected (HTTP 403)

### Requirement: CSRF protection disabled
The system SHALL disable the Jenkins CSRF crumb issuer so that internal service-to-service HTTP calls can trigger jobs without a pre-flight crumb fetch.

#### Scenario: Job trigger without crumb header succeeds
- GIVEN CSRF protection is disabled
- WHEN an HTTP POST to trigger a job is made on port 8080 without an `X-Jenkins-Crumb` header
- THEN the job is triggered successfully (HTTP 201)

#### Scenario: CSRF issuer is null after startup
- GIVEN Jenkins completes its startup sequence
- WHEN the init script runs
- THEN `Jenkins.getInstance().getCrumbIssuer()` returns null

### Requirement: Security bootstrapped via init script
The system SHALL apply security configuration at startup via a Groovy init script placed in `/var/jenkins_home/init.groovy.d/`.

#### Scenario: Security is active before any user interaction
- GIVEN Jenkins completes its startup sequence
- WHEN the first HTTP request arrives
- THEN the security realm and authorisation strategy are already configured
