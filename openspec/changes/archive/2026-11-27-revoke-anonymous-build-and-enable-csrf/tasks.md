## 1. Init script

- [x] 1.1 Remove the `Item.BUILD` and `Item.CANCEL` grants for `anonymous` from `basic-security.groovy`; anonymous `Item.READ` is later removed by 1.5
- [x] 1.2 Replace `instance.setCrumbIssuer(null)` with `new DefaultCrumbIssuer(true)` and import `hudson.security.csrf.DefaultCrumbIssuer`
- [x] 1.3 Update the comment block to state the new posture (anonymous has no permissions; CSRF on, client IP excluded for proxy compatibility)
- [x] 1.4 Replace `HudsonPrivateSecurityRealm` with `ReverseProxySecurityRealm` (header mode, `X-Forwarded-User` / `X-Forwarded-Groups`); add `reverse-proxy-auth-plugin` to `plugins.txt`
- [x] 1.5 `ProjectMatrixAuthorizationStrategy`: service identity and group `admin` → Administer; group `power_user` → Overall/Read, Job/Read, Job/Build, Job/Cancel; group `authenticated` → Overall/Read only; anonymous → nothing. Per-job grants (owner, `team-<id>`) are written by the webapp
- [x] 1.6 Dockerfile seeds the init script as `/usr/share/jenkins/ref/init.groovy.d/basic-security.groovy.override` so existing homes re-copy it on every start
- [x] 1.7 All shipped `nita-cmd jenkins` REST operations (`jobs create/delete/get/enable/disable/ls`, `plugins ls/details`, `version`, `whoami`) use `X-Forwarded-User`; POST requests fetch and submit a crumb with the response cookie.
- [x] 1.8 Update backup and restore helpers to list plugins and restore view membership through the REST API; fail on HTTP errors instead of invoking `jenkins-cli.jar`.
- [x] 1.9 Remove `JENKINS_PASS` from the Jenkins image and Compose environment; document that supported clients use the service identity and crumbs.

## 2. Documentation

- [x] 2.1 Add a release note to `README.md`: anonymous build/cancel removed, CSRF protection enabled, what this means for operators who used *Build Now* without logging in

## 3. Verification

- [x] 3.1 Build the image and start it with an empty `jenkins_home`; confirm the init script logs no Groovy errors
- [x] 3.2 `curl -X POST http://localhost:8080/jenkins/job/<job>/build` with no credentials → 403
- [x] 3.3 `curl -H "X-Forwarded-User: $JENKINS_USER" http://localhost:8080/jenkins/crumbIssuer/api/json` → 200 with a crumb
- [x] 3.4 `curl http://localhost:8080/jenkins/job/<job>/api/json` with no credentials → 403 (anonymous read removed by 1.5)
- [x] 3.5 With the webapp compose stack: entrypoint bootstrap (`configure_jenkins.py`, `add_jenkins_job.py`) succeeds; `POST /api/v1/networks/{id}/trigger/{action_id}/` → 202 and the build runs; SSE console streams; Robot summary renders
  - Verified with locally built `nita-jenkins` and `nita-webapp` images in Compose behind the Traefik proxy: bootstrap created `network_template_mgr` and `network_type_validator` (`HTTP 200`); trigger → `202`; build `SUCCESS` with `UserIdCause`; SSE streamed for about 19 s until `event: done`; Robot summary `{"available":true,"total":4,"passed":3,"failed":1,…}`.
- [x] 3.6 Restart a container with a pre-existing `jenkins_home` and confirm the strategy and issuer converge to the new values
- [x] 3.8 Live on Kubernetes: `whoAmI` reflects `X-Forwarded-User`/`X-Forwarded-Groups`; forwarded user's build records `UserIdCause`; role `user` cannot reach `/manage/`; `admin:admin` Basic auth → 401
- [x] 3.9 Live on Kubernetes (project matrix): role `user` sees only own/team jobs (others 404), team member read-only (build 403), owner build 201, power user/admin see all, anonymous root 403, management jobs 404 for role `user`
- [x] 3.10 Unit-test the REST helper's identity header, cookie-backed crumb flow, argument encoding and HTTP error handling; run the helper tests in the image workflow and smoke-test the installed helper.
- [x] 3.7 `openspec validate revoke-anonymous-build-and-enable-csrf --strict` passes
