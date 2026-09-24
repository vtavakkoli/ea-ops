<p align="center"><img src="docs/assets/ea-ops.svg" width="80" height="80" alt="EA Ops connected architecture icon"></p>

# EA-Ops

**Git-native Enterprise Architecture Operations — model, validate, review, govern, and publish architecture as code.**

EA-Ops brings the operating model of modern engineering to Enterprise Architecture. Architecture facts live in Git as simple YAML objects and relationships. Deterministic rules validate the model. Pull requests become architecture change requests. `main` represents the approved architecture. The same source generates an interactive architecture portal and architecture-quality report.

> **Model → Validate → Review → Govern → Publish**

## A workspace for everyday architecture

**Python 3.10+ · PyYAML · YAML models · Vanilla JavaScript · SVG · GitHub Actions**

Find the system you need, see who owns it, inspect its dependencies, and bring a clear shortlist to your next architecture review.

| Everyday task | Where to start |
| --- | --- |
| Find a system or its owner | **Catalog**: search names, IDs, descriptions, and owners |
| Prepare a review | Filter by layer, owner, favorites, or high / critical assets |
| Return to your work | Star objects and use **Recently opened** on the overview |
| Share architecture context | Open an object and choose **Copy direct link** |
| Take a shortlist into a meeting | **Export CSV** exports the current catalog filters |
| Check model health | **Review priorities** and **Governance** |
| Inspect connections | **Explore dependencies**, then choose one to three hops |

Press **/** to focus search, type a query, and press **Enter**. The portal runs without a frontend build step or external JavaScript services. Favorites and recent items stay in this browser; reviewed YAML in Git remains the shared source of truth.

[Read the daily workflow guide](docs/daily-workflow.md).

## Why EA-Ops

Traditional EA repositories often separate the model from the change process. EA-Ops deliberately reuses Git for identity, access, review history and approvals, while the framework focuses on architecture semantics and governance.

- **Flexible model** — objects and relationships are data, not hard-coded UI forms.
- **ArchiMate-ready** — ships with a pragmatic ArchiMate 3.2 profile and allows custom metamodel packs.
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

## ArchiMate 3.2 notation-aware portal

The generated repository portal renders architecture elements according to their semantic type instead of drawing every object as a generic rectangle. It includes a built-in **Notation** page so architects can inspect the supported visual vocabulary directly in the generated site.

The profile now covers the element families used by the ArchiMate 3.2 reference cards:

- **Strategy** — Resource, Capability, Value Stream, Course of Action
- **Business** — Actor, Role, Collaboration, Interface, Process, Function, Interaction, Event, Service, Object, Contract, Representation, Product
- **Application** — Component, Collaboration, Interface, Function, Interaction, Process, Event, Service, Data Object
- **Technology & Physical** — Node, Device, System Software, Collaboration, Interface, Path, Communication Network, Function, Process, Interaction, Event, Service, Artifact, Equipment, Facility, Distribution Network, Material
- **Motivation** — Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value
- **Implementation & Migration** — Work Package, Deliverable, Implementation Event, Plateau, Gap
- **Composite / connector concepts** — Grouping, Location and Junction

Relationship rendering follows the ArchiMate visual grammar for **Composition, Aggregation, Assignment, Realization, Serving, Access, Influence, Triggering, Flow, Specialization and Association**. Junctions are stored by EA-Ops as graph nodes so relationship routing can remain representable in YAML.

Relationship presentation properties can make the notation more precise:

```yaml
- id: rel.read-customer
  type: Access
  source: process.review-customer
  target: data.customer
  properties:
    accessType: read       # access | read | write | read-write

- id: rel.driver-goal
  type: Influence
  source: driver.digital-first
  target: goal.self-service
  properties:
    strength: "++"

- id: rel.context
  type: Association
  source: capability.service-delivery
  target: stakeholder.customer
  properties:
    directed: true
```

For Access, EA-Ops keeps the model direction from behavior/active structure to passive structure while the visual arrow reflects `read`, `write` or `read-write` access.

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

`eventKind` is an **EA-Ops presentation extension**, not a new ArchiMate element type. The interactive portal recognizes `message`, `timer`, `signal`, `manual`, and `error` and adds a small visual cue while retaining the semantic event type.

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
- drag-and-drop movement of architecture objects with relationship rerouting;
- grid snapping, zoom controls and architect-curated Git positions;
- automatic browser-local draft persistence while an architect experiments;
- **Reset to Git** to restore committed coordinates;
- **Auto layout** to recalculate a clean layout;
- **Copy layout YAML** and **Download YAML** to persist coordinates;
- **Edit view in GitHub** to open the actual view file and commit the exported layout through the normal Git/PR workflow.

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

The companion repository [`vtavakkoli/ea-ops-example`](https://github.com/vtavakkoli/ea-ops-example) models the fictional Metroville Digital Permit Service. It demonstrates an event-driven permit journey, document representations, access modes, influence strength, applications, data, technology, motivation, governance, interactive layouts and automated GitHub Pages publishing.

## Project status

EA-Ops is an **alpha reference implementation**. The built-in profile checks relationship combinations against the pinned Archi 3.2 relationship matrix. This is not a claim of Open Group certification or complete conformance to every normative ArchiMate constraint. The metamodel boundary allows stricter and future profiles to be versioned independently.

## Roadmap

- Complete normative ArchiMate relationship-rule pack
- Semantic model diff for PRs
- Architecture-owner → reviewer mapping
- Generated CODEOWNERS / reviewer suggestions
- GitHub-assisted layout commit / PR creation
- Cross-repository model composition
- Architecture decision records and standards catalog
- Signed releases and PyPI publication

## License

Apache License 2.0. See [LICENSE](LICENSE).


## Research evaluation and reproducibility

EA-Ops includes a publication-oriented benchmark harness under [`benchmarks/`](benchmarks/). It evaluates validation accuracy, controlled fault detection, graph-impact analysis, runtime, peak memory, report generation, and portal generation over deterministic synthetic architectures from **100 to 100,000 objects**.

The canonical experiment is [`.github/workflows/research-evaluation.yml`](.github/workflows/research-evaluation.yml). Run it manually with **Actions → IEEE Research Evaluation → Run workflow**, or push a tag matching `research-*`. The workflow stores raw CSV measurements, runner metadata, publication-ready summary tables, and PDF figures as GitHub Actions artifacts. A `research-*` tag also attaches the reproducibility bundle to the corresponding GitHub Release.

Fault injection and ground-truth generation are deliberately separated from the EA-Ops validator implementation. Generated models and raw results are not committed; they are deterministically regenerated from documented seeds.

See [benchmarks/README.md](benchmarks/README.md) for the methodology, metrics, cloud-runner limitations, and local reproduction commands.
