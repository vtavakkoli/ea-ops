# IEEE Access revision evidence

This is an engineering revision candidate. It does not imply acceptance, practitioner validation, an archival DOI, or production deployment.

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

## Remaining external evidence

1. Complete an archival deposit for the original evaluated commits and the revised source/data; record the issued DOI(s). `.zenodo.json`, `CITATION.cff`, and `ARCHIVAL.md` prepare this, but no DOI exists yet.
2. Conduct genuine practitioner sessions if claiming usability, effort reduction, or governance value. `practitioner-protocol.md` and the empty CSV template support collection; no responses have been invented.
3. Authors should check the clean manuscript, highlighted PDF, and point-by-point response before resubmission. Do not describe the package as fully ready while external evidence remains outstanding.

## Observed revision outcome

The complete local 100,000-object / 200,000-relationship protocol finished: validation median 118.783 s, undirected impact median 1066.254 ms, report median 1.995 s, portal median 2.898 s, maximum process peak RSS 1461.9 MiB, total benchmark child elapsed 484.3 s (generation excluded). These are three-repetition local measurements, not a replacement for the original 30-repetition hosted protocol. Legacy CSV `_mb` names represent MiB (KiB / 1024 on Linux).

Source variants and final file digests are recorded in `measured-source-sha256.json`; a depth-argument type guard and package-version metadata changed during collection without changing the timed default paths.
