## Context

`basic-security.groovy` is a Jenkins init script that runs at every container startup from `/var/jenkins_home/init.groovy.d/`. It currently:
1. Detects whether the admin user exists using `if "{{ jenkins_admin_username }}" in users_s` — a Jinja2 placeholder that is **never substituted**, so this condition is always `false`
2. Sets `FullControlOnceLoggedInAuthorizationStrategy`, which silently blocks all unauthenticated requests, including internal service calls from the webapp
3. Installs no CSRF issuer override, leaving the default crumb issuer active

The webapp (`nita-webapp`) calls Jenkins via its internal HTTP port 8080 to trigger pipeline jobs. With the current authorisation strategy it receives 403 on every call unless it provides admin credentials — which the new webapp architecture deliberately avoids.

## Goals / Non-Goals

**Goals:**
- Anonymous callers on port 8080 can trigger, read, and cancel jobs — nothing more
- CSRF is disabled so callers don't need a two-step crumb-then-trigger flow
- Admin account bootstrap works correctly: create on first boot, update password on subsequent boots
- External users on port 8443 still authenticate via `HudsonPrivateSecurityRealm`

**Non-Goals:**
- Role-based access beyond anonymous job permissions (future work)
- Restricting which jobs anonymous users can trigger — matrix is applied globally
- Any change to how Jenkins is networked (port isolation is handled in `nita` repo via `NetworkPolicy`)

## Decisions

### GlobalMatrixAuthorizationStrategy over other strategies
**Decision:** Use `GlobalMatrixAuthorizationStrategy` with explicit anonymous permissions.

**Rationale:** This is the standard Jenkins approach for fine-grained anonymous access. It allows exactly three permissions to be granted (`Job/Build`, `Job/Read`, `Job/Cancel`) while leaving all other actions (configure, admin, credentials) restricted to authenticated users.

**Alternatives considered:**
- `FullControlOnceLoggedInAuthorizationStrategy` (current) — blocks all anonymous access; rejected
- `AuthorizationStrategy.UNSECURED` — grants everyone full admin; unacceptable security posture
- `ProjectMatrixAuthorizationStrategy` — per-job permissions; unnecessary overhead for a uniform grant

### Disable CSRF rather than teach the webapp to fetch crumbs
**Decision:** `instance.setCrumbIssuer(null)` to remove CSRF protection.

**Rationale:** CSRF protection defends against cross-site request forgery in browser sessions that use cookies. Jenkins's internal HTTP port 8080 is not mapped to the host and is only reachable from within the Docker/k8s network. The webapp communicates via direct HTTP without a browser session, so CSRF crumbs provide no security benefit and add latency and complexity.

**Alternatives considered:**
- Teach the webapp to fetch crumbs — adds a round-trip per trigger, and the crumb endpoint itself requires authentication in some Jenkins versions
- Keep CSRF enabled and pass `X-Jenkins-Crumb` header — fragile; crumbs expire with session

### Fix the Jinja2 bug: compare against `env.JENKINS_USER`
**Decision:** Replace `if "{{ jenkins_admin_username }}" in users_s` with `if env.JENKINS_USER in users_s`.

**Rationale:** The Groovy script is not processed by Jinja2 at runtime — it is `COPY`ed into the image verbatim. The placeholder `{{ jenkins_admin_username }}` is always the literal string, which is never in the user list, so the create branch runs every restart and silently re-creates the admin account (idempotent but noisy and misleading). Replacing with `env.JENKINS_USER` correctly reads the environment variable.

## Risks / Trade-offs

- **[Risk] Anonymous Job/Build is broad** — any pod that can reach port 8080 can trigger any job → Mitigated by the `NetworkPolicy` in `nita` repo (step 2 of the cross-repo plan) which restricts port 8080 ingress to the webapp pod only
- **[Risk] Disabling CSRF weakens browser-session protection** — if port 8080 were ever exposed to a browser context, CSRF attacks become possible → Mitigated by port 8080 never being mapped to the host in Docker Compose or accessible externally via the k8s NetworkPolicy
- **[Risk] Init script runs on every restart** — any error in the Groovy script prevents Jenkins from starting → Mitigated by keeping the script minimal and testing in a local container before deploying

## Migration Plan

1. Update `basic-security.groovy` with the three changes above
2. Rebuild the Docker image: `./build_container.sh`
3. Redeploy the Jenkins container: `nita-cmd_jenkins_down && nita-cmd_jenkins_up`
4. Verify: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/job/<any-job>/api/json` should return 200 (not 403)
5. Verify admin login on https://localhost:8443 still works

**Rollback:** Revert `basic-security.groovy`, rebuild, and redeploy. No persistent state is changed — the init script only affects in-memory Jenkins config on startup.

## Open Questions

- None — all decisions resolved by the cross-repo plan.
