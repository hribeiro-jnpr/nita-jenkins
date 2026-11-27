## MODIFIED Requirements

### Requirement: Jenkins CLI endpoint includes the /jenkins path prefix
Every shipped `nita-cmd jenkins` operation SHALL use the Jenkins REST API under
the `/jenkins` path prefix and assert `JENKINS_USER` with
`X-Forwarded-User`. State-changing requests SHALL fetch and submit a CSRF crumb.
They SHALL preserve cookies across the crumb request and the corresponding
state-changing request.
The commands SHALL NOT use `jenkins-cli.jar` or password-based authentication.

#### Scenario: CLI jar targets the prefixed endpoint
- GIVEN an operator runs a shipped `nita-cmd jenkins` operation
- WHEN it sends a request to Jenkins
- THEN the request targets the `/jenkins` REST API and asserts
  `X-Forwarded-User: $JENKINS_USER`
- AND it sends no password or Basic Authorization header

#### Scenario: No CLI command targets the bare root endpoint
- GIVEN the full set of shipped `nita-cmd jenkins` operations
- WHEN their Jenkins endpoints are inspected
- THEN none targets the server at the bare root path
- AND each state-changing command fetches and submits a crumb with its session
  cookie
