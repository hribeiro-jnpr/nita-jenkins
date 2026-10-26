## MODIFIED Requirements

### Requirement: Full-control-once-logged-in authorisation
The system SHALL configure `GlobalMatrixAuthorizationStrategy` granting the service identity (the user named by `JENKINS_USER`) and the group `admin` `Overall/Administer`; granting the group `authenticated` `Overall/Read`, `Job/Read`, `Job/Build` and `Job/Cancel`; and granting anonymous users `Overall/Read` and `Job/Read` only (`Overall/Read` is the prerequisite for reaching any page; `Job/Read` alone yields HTTP 403). Anonymous users SHALL NOT hold `Job/Build`, `Job/Cancel`, or any other permission. Starting or aborting a build SHALL require an authenticated principal.

#### Scenario: Authenticated user has full access
- GIVEN a request is authenticated as the service identity or as a user in the `admin` group
- WHEN they attempt to create, run, configure, or delete a job
- THEN the action is permitted

#### Scenario: Authenticated non-admin user can build but not administer
- GIVEN a request is authenticated as a user whose only group is `user` or `power_user`
- WHEN they trigger or cancel a build with a valid crumb
- THEN the action is permitted
- AND a request to `/manage/` is rejected (HTTP 403)

#### Scenario: Anonymous user can trigger, read, and cancel jobs
- GIVEN no authentication credentials are provided
- WHEN HTTP requests to read a job, trigger a build, and cancel a build are
	made on port 8080
- THEN the read request is permitted (HTTP 200)
- AND the trigger and cancel requests are rejected (HTTP 403)

#### Scenario: Anonymous user can read jobs and builds
- GIVEN no authentication credentials are provided
- WHEN an HTTP GET for a job page, a build page, a console log, or `/api/json` is made on port 8080
- THEN the request is permitted (HTTP 200)

#### Scenario: Anonymous user cannot trigger a build
- GIVEN no authentication credentials are provided
- WHEN an HTTP POST to `/job/<job>/build` or `/job/<job>/buildWithParameters` is made on port 8080
- THEN the request is rejected (HTTP 403) and no build is queued

#### Scenario: Anonymous user cannot cancel a build
- GIVEN no authentication credentials are provided and a build is running
- WHEN an HTTP POST to `/job/<job>/<build>/stop` is made on port 8080
- THEN the request is rejected (HTTP 403) and the build continues

#### Scenario: Anonymous user cannot access admin functions
- GIVEN no authentication credentials are provided
- WHEN an HTTP request to configure Jenkins, manage credentials, or access system settings is made
- THEN the request is rejected (HTTP 403)

## REMOVED Requirements

### Requirement: CSRF protection disabled
**Reason**: The grant existed so the webapp could trigger builds without a pre-flight crumb. The webapp now authenticates and fetches a crumb for every build request, so disabling CSRF protection only removes a defence for operators using the Jenkins UI.
**Migration**: Clients that POST to Jenkins must fetch a crumb from `/crumbIssuer/api/json` on the same HTTP session and send it in the header named by `crumbRequestField`. The webapp (`CrumbRequester`) and its bootstrap scripts already do this; `jenkins-cli.jar` does not require a crumb.

## ADDED Requirements

### Requirement: Identity is asserted by the reverse proxy
The system SHALL use the Reverse Proxy Auth realm in header mode: username from
`X-Forwarded-User`, groups from `X-Forwarded-Groups` (`|`-delimited); requests
without the header are anonymous. Jenkins SHALL hold no local passwords, and
Basic authentication SHALL only be honoured with an API token.

#### Scenario: Forwarded user is authenticated with their groups
- GIVEN a request on port 8080 carries `X-Forwarded-User: alice` and `X-Forwarded-Groups: power_user`
- WHEN `/whoAmI/api/json` is requested
- THEN Jenkins reports `name: alice` with authorities `authenticated` and `power_user`

#### Scenario: Build started by a forwarded user is attributed to them
- GIVEN a request carrying `X-Forwarded-User: alice` and a valid crumb
- WHEN it POSTs to `/job/<job>/build`
- THEN the build is queued with a `UserIdCause` whose `userId` is `alice` (*Started by user alice*)

#### Scenario: Password Basic auth is not accepted
- GIVEN a request carries `Authorization: Basic` with `JENKINS_USER:JENKINS_PASS`
- WHEN it requests `/manage/`
- THEN the request is rejected (HTTP 401)

#### Scenario: Existing home converges to the header realm
- GIVEN a `jenkins_home` volume persisted by a previous release that used `HudsonPrivateSecurityRealm`
- WHEN the container starts
- THEN the entrypoint re-copies `init.groovy.d/basic-security.groovy` from the image (`.override`) and `config.xml` records the Reverse Proxy Auth realm and the group-based matrix

### Requirement: CSRF protection enabled behind a reverse proxy
The system SHALL install a `DefaultCrumbIssuer` with `excludeClientIPFromCrumb` set to `true` at startup, so that state-changing HTTP requests require a valid crumb and crumbs remain valid when Jenkins is reached through a reverse proxy.

#### Scenario: Crumb issuer is active after startup
- GIVEN Jenkins completes its startup sequence
- WHEN the init script has run
- THEN `Jenkins.getInstance().getCrumbIssuer()` is a `DefaultCrumbIssuer` whose `isExcludeClientIPFromCrumb()` returns `true`

#### Scenario: Authenticated build without crumb is rejected
- GIVEN valid admin credentials
- WHEN an HTTP POST to trigger a job is made on port 8080 without a crumb header
- THEN the request is rejected (HTTP 403)

#### Scenario: Authenticated build with crumb succeeds
- GIVEN valid admin credentials
- WHEN the client fetches `/crumbIssuer/api/json` and POSTs to trigger a job on the same HTTP session with the returned crumb header
- THEN the job is queued (HTTP 201)

#### Scenario: Crumb survives the proxy hop
- GIVEN a client reaches Jenkins through the nginx reverse proxy at `/jenkins/`
- WHEN it fetches a crumb and posts a build with it
- THEN the build is queued, regardless of which proxy connection carried each request
