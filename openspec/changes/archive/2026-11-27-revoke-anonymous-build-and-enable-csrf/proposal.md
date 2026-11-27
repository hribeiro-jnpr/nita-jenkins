## Why

`basic-security.groovy` grants the `anonymous` principal `Job/Build`,
`Job/Read` and `Job/Cancel`, and disables the CSRF crumb issuer. Both were
introduced so the webapp could trigger jobs without credentials. The webapp no
longer does that: every Django→Jenkins call asserts its service or acting-user
identity through the reverse-proxy headers and obtains a crumb before building
(`nita-webapp` capability `jenkins-trigger-security`), and the one remaining
unauthenticated call — the console stream — is fixed in the companion
`nita-webapp/gate-jenkins-behind-webapp-session` change.

What remains is pure exposure. Jenkins is reverse-proxied at `/jenkins/` and,
in the Kubernetes deployment, also published directly on host port 8443. With
the current grants, anyone who can open a TCP connection to either can start or
abort any build with a single unauthenticated `POST`, and no CSRF protection
stands between a logged-in operator's browser and a cross-site request that does
the same.

## What Changes

- **Identity comes from the proxy.** The private user database is replaced by
  the Reverse Proxy Auth realm in header mode: `X-Forwarded-User` is the user,
  `X-Forwarded-Groups` carries the webapp role and one `team-<id>` group per
  team. No passwords live in Jenkins; Basic auth only works with an API token.
- **Authorisation mirrors the webapp.** A project-based matrix grants `admin`
  Administer, `power_user` read/build/cancel on every job and `authenticated`
  Overall/Read only; each per-network job carries its own matrix (owner
  read/build/cancel, team read) written by the webapp. Anonymous has no access;
  management jobs are reachable only by admins/power users.
- **CSRF protection is enabled.** The init script installs a
  `DefaultCrumbIssuer` with `excludeClientIPFromCrumb=true` so crumbs remain
  valid across the reverse proxy hop. Build requests must carry a crumb — which
  the webapp already does via `CrumbRequester`, and the bootstrap scripts
  already fetch one when an issuer is present.
- **Specification is corrected.** The `jenkins-security` capability currently
  *requires* the anonymous grants and *requires* CSRF to be disabled. Those
  requirements are replaced.

Jenkins is only reachable through the webapp-gated proxy and from the webapp
pod (NetworkPolicy), which is the trust precondition of header-based identity.

## Capabilities

### Modified Capabilities

- `jenkins-security`: header-based security realm; project-based matrix that
  mirrors webapp roles, ownership and teams; anonymous has no access; the CSRF
  crumb issuer is enabled and configured for operation behind a reverse proxy.

## Impact

- **Files:** `basic-security.groovy` (realm, matrix and crumb issuer replaced), `openspec/specs/jenkins-security/spec.md` (via archive),
  `README.md` release notes.
- **Image:** adds `reverse-proxy-auth-plugin` to `plugins.txt`; the Dockerfile
  seeds the init script as `.override`. No port changes.
- **Clients updated in the companion webapp change:** the webapp's
  `invoke_job`, console stream and Robot summary, the bootstrap scripts
  (`ping_jenkins.py`, `configure_jenkins.py`, `add_jenkins_job.py`) and
  `network_template_mgr` assert identity with `X-Forwarded-User` and fetch a
  crumb for POSTs. Password Basic auth and `jenkins-cli.jar -s user:pass@…`
  no longer authenticate. Every shipped `nita-cmd jenkins` REST operation and
  the backup/restore helpers now use `X-Forwarded-User`; state-changing
  requests fetch and submit a crumb. `JENKINS_PASS` is removed from the image
  and Compose environment.
- **Behavioural change for humans:** Jenkins is reached through the
  webapp-gated proxy; a webapp session is the Jenkins session. Without it,
  Jenkins returns 403 for every page, including job reads.
- **Ordering:** this change and
  `nita-webapp/gate-jenkins-behind-webapp-session` are interdependent and SHALL
  be deployed together: the new realm rejects the old webapp's password
  credentials, and the new webapp's identity headers mean nothing to the old
  realm. Deploy `nita/close-jenkins-direct-exposure` first, so the
  NetworkPolicy admits the proxy and the host-port bypass is gone before
  Jenkins trusts forwarded identity headers.
