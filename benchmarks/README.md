# EA-Ops research evaluation

This directory contains the reproducible evaluation harness intended for peer-reviewed publication.

## Experimental design

The full GitHub Actions experiment evaluates deterministic architecture models with **100, 1,000, 10,000, 50,000 and 100,000 objects**. By default each generated model contains approximately two relationships per object plus governance fixtures.

For performance experiments the workflow performs three warm-up runs followed by 30 measured repetitions. Validation includes repository loading, ArchiMate relationship checks and governance rules. Impact analysis is measured separately. Report and portal publication are measured on a smaller number of repetitions because they perform filesystem output.

Reported statistics include mean, median, standard deviation, p95 and a normal-approximation 95% confidence interval where applicable. Raw per-repetition measurements are retained.

## Fault oracle

`inject_faults.py` deliberately does **not** import EA-Ops validator internals. It performs deterministic YAML mutations and writes `ground_truth.json`. The evaluator then compares independently declared expected findings with EA-Ops output.

Fault classes are dangling source, dangling target, invalid ArchiMate relationship, missing owner, missing criticality, duplicate identifier, invalid lifecycle value, and organization-governance violation.

Each fault class is evaluated across 30 deterministic trials. Precision, recall and F1 are computed from expected and observed error tuples `(code, object_id)`.

## Cloud-runner limitation

GitHub-hosted runners are shared infrastructure and therefore have runtime noise. The experiment mitigates this with warm-ups, repeated measurements and distribution statistics. Performance comparisons intended for publication should compare configurations within the same workflow definition and runner class. The environment recorder captures commit SHA, runner metadata, CPU model, memory and Python version.

## Local reproduction

```bash
python -m pip install -e .
python -m pip install -r benchmarks/requirements-research.txt

python benchmarks/generate_model.py --objects 1000 --seed 42 --output generated/model-1000
python benchmarks/benchmark.py --model generated/model-1000 --repetitions 30 --output results/raw/performance-1000.csv

python benchmarks/generate_model.py --objects 100 --seed 1 --output generated/clean
python benchmarks/inject_faults.py --model generated/clean --fault missing_owner --output generated/faults/missing_owner/trial-01
python benchmarks/evaluate_accuracy.py --root generated/faults/missing_owner --output results/raw/accuracy-missing_owner.csv

python benchmarks/aggregate.py --input results/raw --output results
```

For the canonical research artifact, use **Actions → IEEE Research Evaluation → Run workflow** or create a tag matching `research-*`. The workflow uploads raw CSVs, environment JSON, summary tables and PDF figures. Research tags additionally attach the complete result bundle to a GitHub Release.
