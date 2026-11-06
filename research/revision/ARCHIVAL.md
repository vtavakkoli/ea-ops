# Archival release checklist

Status: prepared; no archival deposit or DOI has been completed by this revision.

Preserve the original experiment separately from the revised implementation:

| Original component | Immutable commit | Workflow run |
| --- | --- | --- |
| EA-Ops 0.2.0 evaluation | d3ba12e3105b9edbe294d98059e611ccefb8820b | 35993083302 |
| Metroville scenario evaluation | 59fe34511b830f5181e7782d6b9d3fbaf78d9227 | 35990375878 |

1. Check for an existing `v0.2.0` tag before creating one; never move a published tag. If available, create it at the original evaluated framework commit and use an unambiguous case-study tag at the evaluated companion commit.
2. Deposit source archives for those exact commits, recovered raw CSV/environment data, scenario patches, original timeout log, and a manifest containing run URLs, versions, and checksums in Zenodo or another appropriate permanent archive. GitHub artifacts have retention limits and are not sufficient permanent preservation.
3. After reviewing/merging the revision, create a separate revised release, such as `v0.3.0`, pinned to its actual source and data. Do not label revised code as the originally evaluated 0.2.0 implementation.
4. Reserve then publish the archive record through the author's authenticated account. Copy the actual version DOI into the manuscript, response, and citation metadata; never use a fabricated/reserved-only DOI as a completed deposit.
5. Verify the public landing page and archived bytes, and include both repository commit identifiers. Only then mark the archival reviewer request resolved.

The workflow can attach a research results bundle to a `research-*` GitHub release. That release attachment alone does not mint a DOI. `.zenodo.json` supplies descriptive metadata; account linking/deposition remains necessary.
