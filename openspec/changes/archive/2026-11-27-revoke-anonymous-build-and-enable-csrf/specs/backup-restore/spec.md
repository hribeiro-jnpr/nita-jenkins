## MODIFIED Requirements

### Requirement: Backup and restore endpoints include the /jenkins path prefix
The backup and restore scripts SHALL use the Jenkins REST API under the
`/jenkins` path prefix and assert `JENKINS_USER` with `X-Forwarded-User`.
State-changing requests SHALL fetch and submit a CSRF crumb. The scripts SHALL
preserve cookies across the crumb request and the corresponding state-changing
request, and fail explicitly when a Jenkins request fails.

#### Scenario: Backup plugin listing uses the prefixed endpoint
- GIVEN `backup-jenkins-in.sh` lists installed plugins via the REST API
- WHEN it requests the plugin list
- THEN it calls the `/jenkins` endpoint with the service identity and no
  password or Basic Authorization header

#### Scenario: Restore views script uses the prefixed base URL
- GIVEN `restore-jenkins-views.py` restores view membership through the Jenkins HTTP API
- WHEN it sends a state-changing request
- THEN it uses the `/jenkins` base URL with the service identity and a CSRF crumb
- AND it preserves the session cookie returned by the crumb request
- AND it reports an HTTP failure instead of silently succeeding
