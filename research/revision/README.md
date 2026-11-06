# IEEE Access revision evidence

EA-Ops is an initial open-source engineering contribution, accompanied by a preprint with DOI [10.48550/arXiv.2609.30593](https://doi.org/10.48550/arXiv.2609.30593). The present evaluation covers the implementation and reproducible benchmarks; organizational testing is planned as future work.

## What is implemented

- A single-pass report index replaces full-edge scans for each application/process/data row. The Metroville report is byte-identical to the original renderer (`report-equivalence.json`).
- Adjacency BFS preserves default undirected reachability and adds explicit dependency policy, direction/type filters, depth bounds, and explanations.
- Semantic snapshot differences and before/after review scope preserve deleted dependency paths and treat owner/name/description edits locally under a declared heuristic.
- The companion repository runs all ten original scenarios against independent raw-YAML oracles and demonstrates three cross-layer architecture states.
- The regression evaluator requires exact emitted/expected error-set equality. Its legacy P/R/F1 columns remain machine-compatible, but are not detection-accuracy estimates.
- Benchmark CSVs checkpoint completed phases. A bounded Linux supervisor records elapsed time and sampled process high-water RSS, including failed/timed-out runs. Upload steps run even after failure.

## Evidence separation

`../original/raw/` contains recovered original GitHub artifacts from framework run **35993083302**, commit **d3ba12e3105b9edbe294d98059e611ccefb8820b**. The original companion run is **35990375878**, commit **59fe34511b830f5181e7782d6b9d3fbaf78d9227**. The former 100,000-object job log is preserved. Its process memory was never recorded; no historical RSS value is inferred.

`results/` is a separate local revision experiment: seed 42, one warmup, three measured validation/impact repetitions and three publication builds per size. Each size runs in a fresh process. The safe YAML loader is retained. The environment and raw rows are preserved. Local and original hosted measurements must not be presented as a matched-hardware speedup comparison.

```bash
python -m unittest discover -s tests -v
python -m benchmarks.revision_experiment --generated /tmp/eaops-revision-models
python -m benchmarks.publication_assets --original research/original/raw \
  --revision research/revision/results \
  --scenarios ../ea-ops-example/research/revision/metroville-scenarios.csv \
  --paper /path/to/latex-source
```

Original fault trials use seeds 1–30. Random topology varies; mutation fixtures/sites and detector expectations remain fixed. Report eight checks across 30 topology variants, not 240 independent real-world defects. Undirected oracle agreement checks connected-component implementation; typed oracle agreement checks the declared policy, not business-impact validity.

## Scope and planned evaluation

An evaluation by the City of Vienna, Wien Digital (Municipal Department 01, MA 01), is planned. It has not yet been performed and is future work, rather than a prerequisite imposed on the bounded implementation and benchmark claims in this initial article. Author Vahid Tavakkoli serves as a Senior Enterprise Architect in that department; this provides professional context and is not a substitute for independent evaluation.

The existing arXiv preprint DOI is **10.48550/arXiv.2609.30593**. Source, data and workflow provenance are public and pinned to exact commits/run IDs. A separate DOI for a versioned software/data deposit is a distinct preservation option; the preprint DOI must not be mislabeled as archiving the software. `ARCHIVAL.md` explains this response to the reviewer's preservation request.

The manuscript and reviewer response retain the distinction between a planned City evaluation and completed technical experiments. No participant results, production deployment, or measured municipal benefit are claimed. The supplied practitioner protocol and empty template support the future evaluation.

## Observed revision outcome

The complete local 100,000-object / 200,000-relationship protocol finished: validation median 118.783 s, undirected impact median 1066.254 ms, report median 1.995 s, portal median 2.898 s, maximum process peak RSS 1461.9 MiB, total benchmark child elapsed 484.3 s (generation excluded). These are three-repetition local measurements, not a replacement for the original 30-repetition hosted protocol. Legacy CSV `_mb` names represent MiB (KiB / 1024 on Linux).

Source variants and final file digests are recorded in `measured-source-sha256.json`; a depth-argument type guard and package-version metadata changed during collection without changing the timed default paths.

The follow-up patch normalizes Access-mode aliases and the legacy `access` property consistently with the portal. The structural benchmark path and the ten preserved scenario outputs are unchanged.
