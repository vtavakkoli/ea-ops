from __future__ import annotations

from pathlib import Path
import html
import json

from .core import RepositoryModel, metrics, validate
from ._portal_html import PORTAL_HTML
from ._portal_css import PORTAL_CSS
from ._portal_js import PORTAL_JS
from ._portal_polish_js import PORTAL_POLISH_JS
from ._workspace import WORKSPACE_CSS, WORKSPACE_JS


_PORTAL_PRESENTATION_CSS = r'''
.diagram-shell:fullscreen{background:#f3f6fa;padding:16px;overflow:auto}
.diagram-shell:fullscreen .diagram{min-height:calc(100vh - 96px)}
.diagram-shell:fullscreen .diagram svg{min-height:calc(100vh - 96px)}
.diagram-toolbar button.icon-action{display:inline-flex;align-items:center;gap:5px}
.diagram-toolbar button:focus-visible,.nav button:focus-visible,.soft:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid rgba(36,87,214,.28);outline-offset:2px}
'''

_PORTAL_PRESENTATION_JS = r'''
function exportCurrentDiagramSvg(){
  if(!diagramState){toast('Open a diagram first');return}
  const host=document.getElementById(diagramState.containerId),svg=host?.querySelector('svg');
  if(!svg){toast('No diagram available to export');return}
  const clone=svg.cloneNode(true);
  clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
  clone.removeAttribute('style');
  clone.querySelectorAll('.dragging').forEach(el=>el.classList.remove('dragging'));
  const xml='<?xml version="1.0" encoding="UTF-8"?>\n'+new XMLSerializer().serializeToString(clone);
  const blob=new Blob([xml],{type:'image/svg+xml;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  const raw=diagramState.view?.name||obj(diagramState.rootId)?.name||diagramState.rootId||'ea-ops-diagram';
  const name=String(raw).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'ea-ops-diagram';
  a.href=url;a.download=name+'.svg';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),0);toast('SVG exported')
}
async function toggleCurrentDiagramFullscreen(){
  if(!diagramState){toast('Open a diagram first');return}
  const shell=document.getElementById(diagramState.containerId)?.closest('.diagram-shell');
  if(!shell){toast('Diagram container not found');return}
  try{
    if(document.fullscreenElement)await document.exitFullscreen();
    else if(shell.requestFullscreen)await shell.requestFullscreen();
    else toast('Fullscreen is not supported by this browser');
  }catch(err){console.warn('EA-Ops fullscreen request failed',err);toast('Fullscreen could not be opened')}
}
function fitCurrentDiagram(){if(!diagramState)return;diagramState.zoom=1;drawDiagram();toast('Diagram fitted to view')}
'''


def render_portal(repo: RepositoryModel, output: str | Path = "site") -> Path:
    """Render the interactive EA-Ops architecture repository portal.

    The generated site is self-contained: no external JavaScript, analytics,
    unload/beforeunload handlers, or embedded credentials. It includes a
    self-contained favicon, Git-aware layout editing, SVG export, fullscreen
    presentation support and a professional lane-based architecture layout.
    """
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
        .replace("__CSS__", PORTAL_CSS + "\n" + _PORTAL_PRESENTATION_CSS + "\n" + WORKSPACE_CSS)
        .replace("__DATA__", data)
        .replace("__JS__", PORTAL_JS + "\n" + PORTAL_POLISH_JS + "\n" + _PORTAL_PRESENTATION_JS + "\n" + WORKSPACE_JS)
    )

    # Keep the core diagram toolbar compact, but add professional presentation
    # and export controls to every generated diagram.
    page = page.replace(
        '<button onclick="downloadLayout()">Download YAML</button><button onclick="editViewGitHub()">Edit view in GitHub ↗</button>',
        '<button onclick="downloadLayout()">Download YAML</button>'
        '<span class="separator"></span>'
        '<button class="icon-action" onclick="fitCurrentDiagram()">Fit</button>'
        '<button class="icon-action" onclick="exportCurrentDiagramSvg()">⇩ Export SVG</button>'
        '<button class="icon-action" onclick="toggleCurrentDiagramFullscreen()">⛶ Fullscreen</button>'
        '<button onclick="editViewGitHub()">Edit view in GitHub ↗</button>',
    )

    target = output_dir / "index.html"
    target.write_text(page, encoding="utf-8")
    return target
