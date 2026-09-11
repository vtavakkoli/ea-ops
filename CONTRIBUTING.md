# Contributing to EA-Ops

EA-Ops uses pull requests for all non-trivial changes. Keep the deterministic core independent of hosted services: GitHub integration belongs in workflows/actions; model validation belongs in the core.

Before opening a PR:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
eaops validate examples/sample-enterprise
```

Please explain the architecture problem, the proposed behavior, compatibility impact and tests. New rules should include a valid and invalid example where practical.
