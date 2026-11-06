# Preprint DOI and software preservation

The EA-Ops preprint is already available with DOI **10.48550/arXiv.2609.30593** at https://arxiv.org/abs/2609.30593. The manuscript cites this existing persistent publication record.

The initial open-source article supplies public source, raw results and immutable experiment provenance:

| Component | Original evaluated commit | Workflow run |
| --- | --- | --- |
| EA-Ops 0.2.0 | d3ba12e3105b9edbe294d98059e611ccefb8820b | 35993083302 |
| Metroville | 59fe34511b830f5181e7782d6b9d3fbaf78d9227 | 35990375878 |

The reviewer requested a tagged software release deposited in a permanent archive. The author's response cites the existing preprint DOI and pinned open artifacts as the preservation provision for this initial engineering contribution, and explicitly states that no separate software/data DOI has been minted. A preprint DOI identifies the paper; it does not itself archive the repository or prove that the requested software deposit was completed.

A separate Zenodo/Software Heritage preservation step can be added later. If used, keep the original evaluated commits distinct from revised releases, never move a published tag, deposit the exact source/data/checksums, and record the actually issued DOI. `.zenodo.json` and `CITATION.cff` prepare that option. A GitHub release attachment alone does not create a DOI.

The City of Vienna evaluation is planned future work. No additional practitioner study is represented as a mandatory precondition for the article's bounded software-engineering claims; reviewers and the editor will assess that scope and response.
