# EA-Ops

**Git-native Enterprise Architecture Operations — model, validate, review, govern, and publish architecture as code.**

EA-Ops brings the operating model of modern engineering to Enterprise Architecture. Architecture facts live in Git as simple YAML objects and relationships. Deterministic rules validate the model. Pull requests become architecture change requests. `main` represents the approved architecture. The same source generates a searchable portal and architecture-quality report.

> **Model → Validate → Review → Govern → Publish**

## Why EA-Ops

Traditional EA repositories often separate the model from the change process. EA-Ops deliberately reuses Git for identity, access, review history and approvals, while the framework focuses on architecture semantics and governance.

- **Flexible model** — objects and relationships are data, not hard-coded UI forms.
- **ArchiMate-ready** — ships with a pragmatic ArchiMate 3.2 starter profile and allows custom metamodel packs.
- **Deterministic validation** — IDs, references, relationships and organization policies are testable in CI.
- **PR-native governance** — architecture changes are reviewed exactly like code changes.
- **Impact analysis** — traverse the architecture graph from changed objects.
- **One source, many views** — generate catalogs, quality reports and a polished static portal.
- **No database required** — clone the repository and the architecture is there.

## v0.1.0

This first release provides the minimum complete operating loop:

```text
YAML model + relationships
          │
          ▼
     eaops validate
          │
          ▼
     Pull Request
          │
    policy / review
          │
          ▼
       main branch
          │
    ┌─────┴─────┐
    ▼           ▼
  report      portal
```

### CLI

```bash
python -m pip install -e .

eaops validate examples/sample-enterprise
eaops summary examples/sample-enterprise
eaops impact examples/sample-enterprise --id app.crm
eaops report examples/sample-enterprise -o reports/sample-architecture-report.md
eaops build examples/sample-enterprise -o site
```

Open `site/index.html` to browse the generated demo portal.

## Repository model

```text
eaops.yaml
model/
  *.yaml              # architecture objects
relationships/
  *.yaml              # graph edges
views/
  *.yaml               # reusable view definitions
rules/
  *.yaml               # organization policy
```

A process is just an object:

```yaml
id: process.customer-onboarding
type: BusinessProcess
name: Customer Onboarding
description: Validate a new customer and activate service access.
properties:
  owner: Customer Operations
  lifecycle: active
  criticality: critical
```

A relationship is equally simple:

```yaml
id: rel.crm-onboarding
type: Serving
source: app.crm
target: process.customer-onboarding
```

A governance rule remains separate from the model:

```yaml
id: OWNER-001
target: {type: BusinessProcess}
require: {properties: [owner]}
severity: error
message: Every business process must have an accountable owner.
```

## Pull-request governance

EA-Ops does **not** invent another user-management system. GitHub/GitHub Enterprise controls users, teams, repository access, branch protection and approvals. EA-Ops adds architecture-aware validation and impact information on top.

> **Git handles collaboration and access. EA-Ops handles architecture semantics and governance.**

Use the reusable Action from a consumer repository:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: vtavakkoli/ea-ops@main
    with:
      root: .
```

## Demo enterprise

`examples/sample-enterprise` models a small service organization with customer onboarding, procurement and incident management, including business roles, capabilities, applications, information and technology. CI validates it and the Pages workflow turns it into the public demonstration portal.

## Project status

EA-Ops v0.1.0 is an **alpha reference implementation**. The bundled ArchiMate 3.2 profile is intentionally pragmatic and does not yet claim complete normative conformance with the full ArchiMate relationship matrix. The metamodel boundary is designed so additional or future profiles can be versioned independently.

## Roadmap

- Complete ArchiMate relationship-rule pack
- Semantic model diff for PRs
- Architecture-owner → reviewer mapping
- Generated CODEOWNERS / reviewer suggestions
- Rich graphical views
- Cross-repository model composition
- Architecture decision records and standards catalog
- Signed releases and PyPI publication

## License

Apache License 2.0. See [LICENSE](LICENSE).
