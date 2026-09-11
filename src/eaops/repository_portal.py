from __future__ import annotations

from pathlib import Path
import html
import json

from .core import RepositoryModel, metrics, validate
from ._portal_html import PORTAL_HTML
from ._portal_css import PORTAL_CSS
from ._portal_js import PORTAL_JS


def render_portal(repo: RepositoryModel, output: str | Path = "site") -> Path:
    """Render the interactive EA-Ops architecture repository portal."""
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)
    issues = validate(repo)
    payload = {
        "config": repo.config,
        "objects": repo.objects,
        "relationships": repo.relationships,
        "views": repo.views,
        "rules": repo.rules,
        "metamodel": repo.metamodel,
        "issues": [issue.as_dict() for issue in issues],
        "metrics": metrics(repo, issues),
    }
    title = html.escape(f"EA-Ops · {repo.config.get('name', 'Architecture Repository')}")
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (
        PORTAL_HTML.replace("__TITLE__", title)
        .replace("__CSS__", PORTAL_CSS)
        .replace("__DATA__", data)
        .replace("__JS__", PORTAL_JS)
    )
    target = output_dir / "index.html"
    target.write_text(page, encoding="utf-8")
    return target
