# Contributing to EA-Ops

EA-Ops uses pull requests for all non-trivial changes. Keep the deterministic core independent of hosted services: GitHub integration belongs in workflows/actions; model validation belongs in the core.

Before opening a PR:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
eaops validate examples/sample-enterprise
```

Please explain the architecture problem, the proposed behavior, compatibility impact and tests. New rules should include a valid and invalid example where practical.

For portal changes, run the browser interaction checks after building the site:

```bash
eaops build . -o site
# Install test tools outside the repository (Node.js is test-only):
npm install --prefix /tmp/eaops-browser-tests playwright@1.58.2
/tmp/eaops-browser-tests/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/eaops-browser-tests/node_modules node tests/browser_smoke.cjs site/index.html
```

The smoke test serves the generated HTML on a temporary loopback port and checks search, combined filters, favorites persistence, direct links, CSV downloads, keyboard navigation, mobile overflow, and unavailable browser storage. `EAOPS_CHROMIUM` can point to an existing Chromium executable. `EAOPS_SCREENSHOTS` can point to an existing output folder for desktop and mobile captures. These commands are for a POSIX shell; on Windows set the environment variables in PowerShell before running Node.
