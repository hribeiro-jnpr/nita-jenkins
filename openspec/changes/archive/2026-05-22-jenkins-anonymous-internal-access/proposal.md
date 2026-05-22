## Why

The `nita-webapp` needs to trigger Jenkins jobs over HTTP (port 8080) without credentials, but Jenkins currently blocks all anonymous access via `FullControlOnceLoggedInAuthorizationStrategy`. This change grants anonymous users the minimum job permissions required for internal service-to-service calls, disables CSRF protection (only meaningful for browser-session auth), and fixes a pre-existing Jinja2 placeholder bug that causes the admin account to be re-created on every container restart.

## What Changes

- **`basic-security.groovy`**: Replace `FullControlOnceLoggedInAuthorizationStrategy` with `GlobalMatrixAuthorizationStrategy` and grant anonymous users `Job/Build`, `Job/Read`, and `Job/Cancel` permissions
- **`basic-security.groovy`**: Disable CSRF by calling `instance.setCrumbIssuer(null)` — crumbs are irrelevant for internal service calls and block the webapp from triggering jobs without a pre-flight crumb fetch
- **`basic-security.groovy`**: Fix the Jinja2 placeholder bug — `{{ jenkins_admin_username }}` is never substituted at runtime, so the `if "{{ jenkins_admin_username }}" in users_s` condition always evaluates to false, causing the admin account create path to run on every restart instead of the update path

## Capabilities

### New Capabilities

<!-- None — this change modifies existing security behaviour only -->

### Modified Capabilities

- `jenkins-security`: Authorisation strategy changes from full-control-once-logged-in to matrix-based; anonymous job permissions added; CSRF disabled; admin user detection logic fixed

## Impact

- `basic-security.groovy` — sole file modified
- Jenkins anonymous users gain `Job/Build`, `Job/Read`, `Job/Cancel` on all jobs; they cannot access configuration, credentials, or admin functions
- External users on port 8443 still see a login page — `HudsonPrivateSecurityRealm` is unchanged; the matrix strategy grants job permissions only, not admin
- The webapp (`nita-webapp`) can remove `JENKINS_USER` / `JENKINS_PASS` credentials from its Jenkins client calls after this change is deployed
- Must be deployed **before** the `nita-webapp` `close-webapp-gaps` change goes live, otherwise all job triggers return 403
