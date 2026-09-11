# EA-Ops

**Git-native Enterprise Architecture Operations — model, validate, review, govern, and publish architecture as code.**

EA-Ops brings the operating model of modern engineering to Enterprise Architecture. Architecture facts live in Git as simple YAML objects and relationships. Deterministic rules validate the model. Pull requests become architecture change requests. `main` represents the approved architecture. The same source generates an interactive architecture portal and architecture-quality report.

> **Model → Validate → Review → Govern → Publish**

## Why EA-Ops

Traditional EA repositories often separate the model from the change process. EA-Ops deliberately reuses Git for identity, access, review history and approvals, while the framework focuses on architecture semantics and governance.

- **Flexible model** — objects and relationships are data, not hard-coded UI forms.
- **ArchiMate-ready** — ships with a pragmatic ArchiMate 3.2 starter profile and allows custom metamodel packs.
- **Deterministic validation** — IDs, references, relationships and organization policies are testable in CI.
- **PR-native governance** — architecture changes are reviewed exactly like code changes.
- **Impact analysis** — traverse the architecture graph from changed objects.
- **Interactive architecture views** — browse, drag, refine and export stable diagram layouts.
- **One source, many views** — generate catalogs, process views, data views, reports and a static portal.
- **No database required** — clone the repository and the architecture is there.

## Operating loop

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
  report   interactive portal
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

Open `site/index.html` to browse the generated portal.

## Repository model

```text
eaops.yaml
model/
  *.yaml              # architecture objects
relationships/
  *.yaml              # graph edges
views/
  *.yaml               # reusable view definitions + optional positions
rules/
  *.yaml               # organization policy
```

A process is an architecture object:

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

## Process events and documents

EA-Ops keeps the semantic model ArchiMate-based. A process event is modeled as a `BusinessEvent`; a document-like human-readable form is modeled as a `Representation` rather than inventing a document element type.

```yaml
- id: event.payment-window-opened
  type: BusinessEvent
  name: Payment Window Opened
  properties:
    owner: Finance
    eventKind: timer

- id: representation.decision-letter
  type: Representation
  name: Permit Decision Letter
  properties:
    owner: Permit Office
    format: PDF
```

`eventKind` is an **EA-Ops presentation extension**, not a new ArchiMate element type. The interactive portal currently recognizes `message`, `timer`, `signal`, `manual`, `error`, and `generic` and renders a distinct event icon while retaining the semantic type `BusinessEvent`.

## Interactive layouts as code

Views can keep architect-curated coordinates in Git:

```yaml
id: view.permit-process
name: Permit Process
root: process.submit-permit
layout:
  direction: LR
  positions:
    event.request-received: {x: 120, y: 235}
    process.submit-permit: {x: 340, y: 235}
    representation.application-pdf: {x: 340, y: 540}
```

The generated portal supports:

- layered automatic layout for process, application, data and technology context;
- drag-and-drop movement of architecture objects;
- automatic browser-local draft persistence while an architect experiments;
- **Reset to Git** to restore committed coordinates;
- **Auto layout** to discard positioning and recalculate a clean layout;
- **Copy layout YAML** and **Download YAML** to persist the refined coordinates through the normal Git/PR workflow.

The Git repository remains the source of truth. Browser-local positioning is intentionally a draft until the exported `layout.positions` is committed and reviewed.

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

## Reference architecture

The companion repository [`vtavakkoli/ea-ops-example`](https://github.com/vtavakkoli/ea-ops-example) models the fictional Metroville Digital Permit Service. It demonstrates an event-driven permit journey, document representations, applications, data, technology, motivation, governance, interactive layouts and automated GitHub Pages publishing.

## Project status

EA-Ops is an **alpha reference implementation**. The bundled ArchiMate 3.2 profile is intentionally pragmatic and does not yet claim complete normative conformance with the full ArchiMate relationship matrix. The metamodel boundary is designed so additional or future profiles can be versioned independently.

## Roadmap

- Complete ArchiMate relationship-rule pack
- Semantic model diff for PRs
- Architecture-owner → reviewer mapping
- Generated CODEOWNERS / reviewer suggestions
- GitHub-assisted layout commit / PR creation
- Cross-repository model composition
- Architecture decision records and standards catalog
- Signed releases and PyPI publication

## License

Apache License 2.0. See [LICENSE](LICENSE).
