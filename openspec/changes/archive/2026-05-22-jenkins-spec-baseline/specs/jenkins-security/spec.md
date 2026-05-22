## ADDED Requirements

### Requirement: Admin user created from environment variables
The system SHALL create a Jenkins admin account using credentials read from `JENKINS_USER` and `JENKINS_PASS` environment variables at first boot.

#### Scenario: Fresh container with no existing users
- **WHEN** Jenkins starts with an empty `jenkins_home` volume
- **THEN** an admin account is created with the username and password from `JENKINS_USER` / `JENKINS_PASS`

### Requirement: Existing admin password update
The system SHALL update the admin user's password if the account already exists, without creating a duplicate account.

#### Scenario: Container restart with pre-existing admin
- **WHEN** Jenkins starts and the admin user already exists in the security realm
- **THEN** the password is updated to the current value of `JENKINS_PASS`

### Requirement: Full-control-once-logged-in authorisation
The system SHALL configure `FullControlOnceLoggedInAuthorizationStrategy` so that any authenticated user has full Jenkins access.

#### Scenario: Logged-in user can perform all operations
- **WHEN** a user authenticates successfully
- **THEN** they can create, run, and delete jobs without additional role assignment

### Requirement: Security bootstrapped via init script
The system SHALL apply security configuration at startup via a Groovy init script placed in `/var/jenkins_home/init.groovy.d/`.

#### Scenario: Security is active before any user interaction
- **WHEN** Jenkins completes its startup sequence
- **THEN** the security realm and authorisation strategy are already configured
