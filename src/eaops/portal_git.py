from __future__ import annotations

from pathlib import Path

from .core import RepositoryModel
from .portal import render_portal as _render_portal


_HEAD_ENHANCEMENTS = r'''
<meta name="application-name" content="EA-Ops">
<meta name="description" content="EA-Ops interactive Enterprise Architecture as Code portal with ArchiMate notation, governed views, reports, and Git-native layout editing.">
<meta name="theme-color" content="#0b1730">
<meta name="color-scheme" content="light">
<meta property="og:type" content="website">
<meta property="og:title" content="EA-Ops Interactive Architecture Portal">
<meta property="og:description" content="Browse Enterprise Architecture as Code with ArchiMate notation, interactive diagrams, governance, and Git-native layouts.">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop stop-color='%236b8cff'/%3E%3Cstop offset='1' stop-color='%232ed2c9'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='64' height='64' rx='15' fill='%230b1730'/%3E%3Crect x='7' y='7' width='50' height='50' rx='12' fill='url(%23g)'/%3E%3Ctext x='32' y='39' text-anchor='middle' font-family='Arial,sans-serif' font-size='22' font-weight='700' fill='%23071124'%3EEA%3C/text%3E%3C/svg%3E">
'''

_STYLE_ENHANCEMENTS = r'''
.diagram-shell:fullscreen{background:#f4f7fb;padding:16px;overflow:auto}
.diagram-shell:fullscreen .diagram{min-height:calc(100vh - 94px)}
.diagram-shell:fullscreen .diagram svg{min-height:calc(100vh - 94px)}
.diagram-toolbar button.icon-action{display:inline-flex;align-items:center;gap:5px}
.diagram-toolbar button:hover{background:#f4f7fb;border-color:#aebbd0}
.diagram-toolbar button.primary:hover{background:#1e4fc6;border-color:#1e4fc6}
'''

_GIT_RUNTIME = r'''
function openLayoutInGitHub(id){
  const state=diagramStates[id];
  const base=EA.config?.repository?.url;
  const branch=EA.config?.repository?.branch||'main';
  const source=state?.view?._source;
  if(!base||!source){flash('Add repository.url to eaops.yaml to enable GitHub editing');return;}
  const editUrl=base.replace(/\/$/,'')+'/edit/'+encodeURIComponent(branch)+'/'+source.split('/').map(encodeURIComponent).join('/');
  const opened=window.open(editUrl,'_blank','noopener,noreferrer');
  if(!opened) flash('Popup blocked — allow popups for this portal to open the GitHub editor');
}

function exportDiagramSvg(id){
  const container=document.getElementById(id);
  const svg=container?.querySelector('svg');
  if(!svg){flash('No diagram available to export');return;}
  const clone=svg.cloneNode(true);
  clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
  clone.querySelectorAll('.dragging').forEach(el=>el.classList.remove('dragging'));
  const source='<?xml version="1.0" encoding="UTF-8"?>\n'+new XMLSerializer().serializeToString(clone);
  const blob=new Blob([source],{type:'image/svg+xml;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url;
  const state=diagramStates[id];
  const label=(state?.view?.name||state?.rootId||'ea-ops-diagram').toString().toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
  a.download=(label||'ea-ops-diagram')+'.svg';
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),0);
  flash('SVG exported');
}

async function toggleDiagramFullscreen(id){
  const container=document.getElementById(id);
  const shell=container?.closest('.diagram-shell');
  if(!shell){flash('Diagram container not found');return;}
  try{
    if(document.fullscreenElement){await document.exitFullscreen();}
    else if(shell.requestFullscreen){await shell.requestFullscreen();}
    else flash('Fullscreen is not supported by this browser');
  }catch(err){
    console.warn('EA-Ops fullscreen request failed',err);
    flash('Fullscreen could not be opened');
  }
}
'''


def render_portal(repo: RepositoryModel, output_dir: str | Path) -> Path:
    """Render the portal and add GitHub-aware editing plus browser-safe polish.

    EA-Ops deliberately keeps the generated portal self-contained: no external
    JavaScript, no analytics, no unload/beforeunload handlers, and no embedded
    credentials. Repository metadata can enable a safe link into GitHub's own
    authenticated editor, while layout drafts remain local until committed.
    """
    out = _render_portal(repo, output_dir)
    html = out.read_text(encoding="utf-8")

    # Prevent the browser's implicit /favicon.ico request on GitHub Pages and
    # provide useful metadata for tabs, bookmarks, link previews, and mobile UI.
    html = html.replace("</head>", _HEAD_ENHANCEMENTS + "\n</head>", 1)
    html = html.replace("</style>", _STYLE_ENHANCEMENTS + "\n</style>", 1)

    # Enhance every interactive diagram with useful export/presentation tools.
    html = html.replace(
        '<button onclick="downloadLayout(\'${containerId}\')">Download YAML</button><span class="status">',
        '<button onclick="downloadLayout(\'${containerId}\')">Download YAML</button>'
        '<button class="icon-action" onclick="exportDiagramSvg(\'${containerId}\')">⇩ Export SVG</button>'
        '<button class="icon-action" onclick="toggleDiagramFullscreen(\'${containerId}\')">⛶ Fullscreen</button>'
        '<button onclick="openLayoutInGitHub(\'${containerId}\')">Edit view in GitHub</button>'
        '<span class="status">',
    )
    html = html.replace("function mountDiagram(", _GIT_RUNTIME + "\nfunction mountDiagram(", 1)
    out.write_text(html, encoding="utf-8")
    return out
