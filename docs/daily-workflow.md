# Daily architecture workflow

## Start locally

```bash
git clone https://github.com/vtavakkoli/ea-ops.git
cd ea-ops
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -e .
eaops validate .
eaops build . -o site
python -m http.server 8000 --directory site --bind 127.0.0.1
```

Open http://localhost:8000. You can also open `site/index.html` directly, but local-file storage and clipboard permissions vary by browser. A stable HTTP URL gives personal shortcuts a consistent location. Stop the local server with Ctrl+C.

## Five-minute review

1. Check **Review priorities** for unassigned owners, critical assets, and governance findings. Counts reflect the generated model, not live monitoring.
2. Open **Catalog**, search for a service or owner, and refine the layer and scope filters. All filters combine.
3. Star the objects you need frequently. Favorites and the last eight opened objects are stored locally per repository and URL path; the dashboard displays up to five of each.
4. Open an object, inspect its metadata and relationships, or choose **Explore dependencies**. One to three hops reveals modeled connections; it does not simulate operational failures.
5. Export the filtered catalog as CSV for a review meeting, or copy an object's direct link for a colleague who can access the same published portal. A localhost or file link only works where that location exists.

## Make a shared change

Edit the corresponding YAML under `model/`, `relationships/`, or `views/`. Validate, inspect impact, and regenerate the portal:

```bash
eaops validate .
eaops impact . --id YOUR_OBJECT_ID
eaops report . -o reports/architecture-report.md
eaops build . -o site
```

Use a real object ID from the catalog in place of `YOUR_OBJECT_ID`. Commit the YAML on a branch and open a pull request. Diagram dragging saves a browser draft; use **Download YAML** and commit the layout to share it. Favorites do not change the architecture model.

## Privacy, persistence, and troubleshooting

- The generated portal is a snapshot. Rebuild after model changes. Browser edits do not update Git automatically.
- Favorites and recent items are stored in `localStorage`, without server synchronization. Clearing site data clears them. If browser storage is blocked, they last for the current session only.
- Search with no matches displays an empty state; **Reset filters** returns to the whole catalog. Unknown object links show the catalog with a notification.
- CSV exports contain the filtered model data. Formula-like cell values are prefixed with an apostrophe to prevent spreadsheet execution; CSV is a review export, not an import or backup format.
- First validation requires the pinned Archi relationship matrix. For offline environments, prefetch its exact bytes from the URL in `src/eaops/data/archimate-3.2.yaml` in the framework repository and set `EAOPS_ARCHIMATE_MATRIX` to that file. The Git blob hash is verified. Do not disable validation to bypass a failed download.
- Publish only architecture information appropriate for your site's audience. Static HTML includes the complete model; page filters do not enforce access control. Use your organization's hosting access controls for private models.

## Interface shortcuts

| Action | Shortcut / control |
| --- | --- |
| Focus global search | `/` outside a form field |
| Search the entire catalog | Enter in global search |
| Clear and leave global search | Escape |
| Open focused cards | Enter or Space |
| Jump past navigation | Tab to **Skip to content** |
| Share an object | **Copy direct link**; manual-copy fallback if clipboard is unavailable |
