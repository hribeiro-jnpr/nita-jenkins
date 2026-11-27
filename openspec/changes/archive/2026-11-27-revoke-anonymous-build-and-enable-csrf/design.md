## Context

`basic-security.groovy` runs from `init.groovy.d` on every start and owns the
whole security posture: it creates/updates the admin account from
`JENKINS_USER`/`JENKINS_PASS`, installs a `GlobalMatrixAuthorizationStrategy`,
nulls the crumb issuer, and sets the location URL. Lines 45–51 are the ones
this change touches:

```groovy
strategy.add(hudson.model.Hudson.ADMINISTER, env.JENKINS_USER)
strategy.add(hudson.model.Item.BUILD, 'anonymous')
strategy.add(hudson.model.Item.READ, 'anonymous')
strategy.add(hudson.model.Item.CANCEL, 'anonymous')
instance.setAuthorizationStrategy(strategy)
instance.setCrumbIssuer(null)
```

Who talks to this Jenkins, and how:

| Client | Auth | Crumb-aware |
|---|---|---|
| webapp Django→Jenkins HTTP clients | `X-Forwarded-User` identity | state-changing requests fetch a crumb |
| webapp bootstrap scripts | `X-Forwarded-User` identity | fetch and submit a crumb |
| in-job `network_template_mgr` REST calls | `X-Forwarded-User` identity | fetch and submit a crumb |
| `nita-cmd jenkins …` REST operations | `X-Forwarded-User: JENKINS_USER` | helper fetches a crumb for POSTs |
| backup and restore helpers | `X-Forwarded-User: JENKINS_USER` | helper fetches a crumb for view updates |
| humans in the Jenkins UI | webapp session forwarded by the proxy | browser form handles it |

Every shipped client uses the header-based realm. State-changing HTTP
operations fetch and send a crumb; no client relies on Jenkins CLI password
authentication or `JENKINS_PASS`.

## Goals / Non-Goals

**Goals**

- No unauthenticated principal can read, start or abort anything.
- Jenkins knows the webapp user (and role/teams) on every request, so builds
  are attributed correctly and per-network visibility matches the webapp.
- CSRF protection is on, and works through the Traefik proxy.
- Existing `jenkins_home` volumes converge to the new realm/matrix on restart.

**Non-Goals**

- Rotating or externalising a Jenkins credential (there is none any more).
- Any change to ports or TLS.

## Decisions

### Decision 1: Header-based realm plus a project-based matrix instead of anonymous read

**Choice:** `ReverseProxySecurityRealm` (header mode) and
`ProjectMatrixAuthorizationStrategy`: service identity and group `admin` →
Administer; `power_user` → Overall/Read, Job/Read, Job/Build, Job/Cancel;
`authenticated` → Overall/Read; anonymous → nothing. Per-network jobs carry an
`AuthorizationMatrixProperty` (owner and `team-<id>` read/build/cancel)
written by the webapp's `network_template_mgr`.

**Rationale:** Anonymous read behind the gate was a stop-gap: it made every
logged-in NITA user equal inside Jenkins, so a regular user could browse and
(while `authenticated` held Build) trigger any other user's jobs — which the
webapp forbids. With identity in the headers the matrix can express the webapp
model directly, and team membership changes apply on the next request because
the groups header is computed per request. Management jobs intentionally have
no per-job grants so regular users cannot drive `operation=delete` on others.

**Rejected:** keeping anonymous `Job/Read` (leaks every job to every user once
per-job grants exist); mirroring webapp users into the private realm (no SSO,
no password sync); per-user API tokens (token lifecycle for every user).

### Decision 2: `DefaultCrumbIssuer(true)`

**Choice:**

```groovy
import hudson.security.csrf.DefaultCrumbIssuer
instance.setCrumbIssuer(new DefaultCrumbIssuer(true))
```

**Rationale:** `DefaultCrumbIssuer` is Jenkins core — no plugin. The boolean is
`excludeClientIPFromCrumb`. With `false`, the crumb is salted with the client
IP as Jenkins sees it; behind a proxy that is the proxy's IP, which is stable,
but the webapp's `CrumbRequester` fetches the crumb from one connection and may
post the build from another, and any change in proxy topology (Traefik, more
replicas) would start producing spurious 403s. `true` removes that fragility
at the cost of binding the crumb to the session only, which is the standard
recommendation for proxied Jenkins.

**Compatibility check against existing clients:** `CrumbRequester`
(jenkinsapi) fetches `/crumbIssuer/api/json` and sends the field it names —
works. The bootstrap scripts do the same with a shared cookie jar — works
(their "404 → proceed without crumb" branch simply stops being taken).
python-jenkins only does GETs here. The NITA command and backup/restore helpers
use the Jenkins REST API with the configured service identity and fetch a crumb
before state-changing requests.

### Decision 3: Spec is rewritten, not patched around

**Choice:** `MODIFY` the authorisation requirement, `REMOVE` the "CSRF
protection disabled" requirement, and `ADD` a "CSRF protection enabled" one.

**Rationale:** The existing spec actively mandates the insecure state. Leaving
those requirements in place with a contradicting addition would make the
capability incoherent. The archive step will replace them in
`specs/jenkins-security/spec.md`.

## Risks / Trade-offs

- **Humans who relied on *Build Now* without logging in.** They now see the
  button greyed out (Jenkins hides actions the principal cannot perform). They
  can log into Jenkins as admin, or — the intended path — use the webapp.
- **An unknown unauthenticated client.** The table above is what the three
  repos contain. If some external automation was posting builds anonymously it
  will start receiving 403 and must be given credentials. That is the point of
  the change.
- **Crumb issuer and the Reverse Proxy Setup monitor.** Enabling crumbs does
  not affect Jenkins's reverse-proxy self-check; the location URL handling is
  unchanged.

## Migration Plan

1. Build the image; start it with an empty `jenkins_home` and with an existing
   one (the init script runs on every boot and overwrites the strategy and
   issuer, so pre-existing installs converge on restart).
2. Verify (see tasks 3.x) anonymous POST build → 403, authenticated crumb fetch
   → 200, webapp trigger → 202 and the build runs, bootstrap scripts succeed.
3. Deploy this hardening first, followed by
  `nita/close-jenkins-direct-exposure`, then
  `nita-webapp/gate-jenkins-behind-webapp-session`. Confirm the proxy can reach
  Jenkins before enabling the session gate.

Rollback: revert `basic-security.groovy`; the next restart restores the
previous grants and nulls the issuer.
