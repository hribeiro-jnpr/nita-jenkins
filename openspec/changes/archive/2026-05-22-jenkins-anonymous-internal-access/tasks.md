## 1. Fix admin user detection bug

- [x] 1.1 In `basic-security.groovy`, replace `if "{{ jenkins_admin_username }}" in users_s` with `if env.JENKINS_USER in users_s`

## 2. Replace authorisation strategy

- [x] 2.1 Remove the `FullControlOnceLoggedInAuthorizationStrategy` block from `basic-security.groovy`
- [x] 2.2 Add `GlobalMatrixAuthorizationStrategy` and grant `hudson.model.Hudson.Administer` to the admin user
- [x] 2.3 Grant anonymous user `hudson.model.Item.Build`, `hudson.model.Item.Read`, and `hudson.model.Item.Cancel` permissions in the matrix strategy

## 3. Disable CSRF

- [x] 3.1 Add `instance.setCrumbIssuer(null)` to `basic-security.groovy` after the authorisation strategy is applied

## 4. Verify correctness

- [x] 4.1 Review the complete updated `basic-security.groovy` to confirm all three changes are present and the Groovy syntax is valid
- [x] 4.2 Confirm the admin account update path (`THEN the password is updated`) is reachable when `env.JENKINS_USER` exists in the user list
- [x] 4.3 Confirm the `instance.save()` call is present after all configuration changes
