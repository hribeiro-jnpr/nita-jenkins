## Context

`nita-jenkins` is the CI/CD engine for the NITA (Network Infrastructure Test Automation) framework. It ships as a custom Docker image built on `jenkins/jenkins:lts-jdk17`, pre-loaded with plugins, Python tooling, and helper scripts. The image is deployed via Docker Compose or Kubernetes and exposes Jenkins over HTTPS on port 8443.

Currently there are no formal specs. Any contributor wanting to modify the image, scripts, or CLI must reverse-engineer intent from code. This change introduces spec files that record the intended behaviour of each capability so future proposals can reference them and CI can detect regressions.

## Goals / Non-Goals

**Goals:**
- Produce one `spec.md` per capability that accurately reflects the **current** implementation
- Specs use present tense to describe what the system does today (not aspirational)
- Each spec is self-contained and human-readable without needing to read the source

**Non-Goals:**
- Fixing bugs, gaps, or design issues found during spec writing — those become separate proposals
- Adding new capabilities
- Introducing any form of automated spec-enforcement tooling (future work)

## Decisions

### One spec file per capability area
**Decision:** Split into 10 capability specs rather than one monolithic file.

**Rationale:** Each capability has distinct owners and change frequency. Fine-grained specs mean a change to the backup scripts only requires reviewing/updating `backup-restore/spec.md`, not re-reading a 500-line document.

**Alternatives considered:** Single `spec.md` — too coarse; hard to link a PR to a specific requirement.

### Spec location: `openspec/specs/<capability>/spec.md`
**Decision:** Follow the openspec convention already established in `nita-webapp`.

**Rationale:** Consistency across the NITA monorepo; openspec CLI tooling expects this layout.

### Spec content: behaviour, not implementation
**Decision:** Specs describe observable inputs, outputs, and constraints — not internals.

**Rationale:** Specs should stay stable when implementation is refactored. A spec saying "the image SHALL install kubectl" survives a change from `apt` to a pre-built binary; one saying "uses `curl -LO …`" does not.

### Capability mapping
| Capability slug | Primary source files |
|---|---|
| `container-image` | `Dockerfile`, `build_container.sh`, `VERSION.txt` |
| `container-runtime` | `docker-compose.yaml` |
| `jenkins-security` | `basic-security.groovy` |
| `jenkins-plugins` | `plugins.txt` |
| `python-toolchain` | `requirements.txt`, `Dockerfile` (pip install step) |
| `job-generation-ansible` | `create_ansible_job_k8s.py` |
| `job-generation-robot` | `robot.py` |
| `yaml-file-writer` | `write_yaml_files.py` |
| `backup-restore` | `backup_script/` |
| `cli-commands` | `cli_scripts/` |

## Risks / Trade-offs

- **Specs may drift from code** → Mitigated by the openspec workflow: every future change proposal must reference and optionally update the relevant spec.
- **Initial specs may miss edge cases** → Acceptable for a baseline; gaps discovered during future proposals become spec amendments.
- **No automated enforcement today** → Specs are advisory. A future change could add linting or contract tests.

## Open Questions

- Should `cli-commands` be one spec or split further (lifecycle vs job management vs backup vs SSL)? Decision deferred — start coarse and split if a spec grows unwieldy.
