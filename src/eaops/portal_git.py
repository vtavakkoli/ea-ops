from __future__ import annotations

from pathlib import Path

from .core import RepositoryModel
from .portal import render_portal as _render_portal


_GIT_RUNTIME = r'''
function openLayoutInGitHub(id){
  const state=diagramStates[id];
  const base=EA.config?.repository?.url;
  const branch=EA.config?.repository?.branch||'main';
  const source=state?.view?._source;
  if(!base||!source){flash('Add repository.url to eaops.yaml to enable GitHub editing');return;}
  const editUrl=base.replace(/\/$/,'')+'/edit/'+encodeURIComponent(branch)+'/'+source.split('/').map(encodeURIComponent).join('/');
  window.open(editUrl,'_blank','noopener');
}
'''


def render_portal(repo: RepositoryModel, output_dir: str | Path) -> Path:
    """Render the portal and add optional GitHub-aware layout editing controls.

    No token or credential is embedded in the static portal. If ``eaops.yaml``
    provides ``repository.url`` (and optionally ``repository.branch``), the
    portal opens the corresponding view file in GitHub's authenticated editor.
    The architect can copy the generated layout YAML and commit it through the
    normal repository/PR workflow.
    """
    out = _render_portal(repo, output_dir)
    html = out.read_text(encoding="utf-8")
    html = html.replace(
        '<button onclick="downloadLayout(\'${containerId}\')">Download YAML</button><span class="status">',
        '<button onclick="downloadLayout(\'${containerId}\')">Download YAML</button>'
        '<button onclick="openLayoutInGitHub(\'${containerId}\')">Edit view in GitHub</button>'
        '<span class="status">',
    )
    html = html.replace("function mountDiagram(", _GIT_RUNTIME + "\nfunction mountDiagram(", 1)
    out.write_text(html, encoding="utf-8")
    return out
