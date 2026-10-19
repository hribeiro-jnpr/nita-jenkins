## 1. Init script

- [ ] 1.1 Remove the `Item.BUILD` and `Item.CANCEL` grants for `anonymous` from `basic-security.groovy`; keep `Item.READ`
- [ ] 1.2 Replace `instance.setCrumbIssuer(null)` with `new DefaultCrumbIssuer(true)` and import `hudson.security.csrf.DefaultCrumbIssuer`
- [ ] 1.3 Update the comment block to state the new posture (anonymous read-only; CSRF on, client IP excluded for proxy compatibility)

## 2. Documentation

- [ ] 2.1 Add a release note to `README.md`: anonymous build/cancel removed, CSRF protection enabled, what this means for operators who used *Build Now* without logging in

## 3. Verification

- [ ] 3.1 Build the image and start it with an empty `jenkins_home`; confirm the init script logs no Groovy errors
- [ ] 3.2 `curl -X POST http://localhost:8080/jenkins/job/<job>/build` with no credentials → 403
- [ ] 3.3 `curl -u $JENKINS_USER:$JENKINS_PASS http://localhost:8080/jenkins/crumbIssuer/api/json` → 200 with a crumb
- [ ] 3.4 `curl http://localhost:8080/jenkins/job/<job>/api/json` with no credentials → 200 (anonymous read retained)
- [ ] 3.5 With the webapp compose stack: entrypoint bootstrap (`configure_jenkins.py`, `add_jenkins_job.py`) succeeds; `POST /api/v1/networks/{id}/trigger/{action_id}/` → 202 and the build runs; SSE console streams; Robot summary renders
- [ ] 3.6 Restart a container with a pre-existing `jenkins_home` and confirm the strategy and issuer converge to the new values
- [ ] 3.7 `openspec validate revoke-anonymous-build-and-enable-csrf --strict` passes
