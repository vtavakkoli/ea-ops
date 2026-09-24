"""Daily workspace enhancements for the dependency-free, static portal."""

WORKSPACE_CSS = r'''
:root{--brand:#385bdd;--bg:#f5f7fb}.mark{background:none;width:44px;height:44px}.mark svg{width:44px;height:44px}.brand{letter-spacing:-.04em}.brand small{letter-spacing:.09em}.hero{background:radial-gradient(ellipse at 92% 95%,#176b70 0,transparent 48%),linear-gradient(115deg,#101e38,#23396a);padding:40px}.hero h1{max-width:900px}.hero p{max-width:700px}.hero:after{pointer-events:none}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px;position:relative;z-index:1}.primary-action,.secondary-action{border:1px solid #8fa5ce;border-radius:10px;padding:12px 18px;font-weight:650;cursor:pointer}.primary-action{background:#a9f3de;color:#102c32;border-color:#a9f3de}.secondary-action{background:#ffffff0d;color:white}.workspace-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin:22px 0}.workspace-grid h2{font-size:17px;margin-bottom:5px}.workspace-grid .panel{box-shadow:none}.workspace-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid var(--line)}.workspace-row:last-child{border-bottom:0}.object-link{border:0;background:none;color:var(--brand);padding:0;text-align:left;font-weight:650;cursor:pointer;overflow-wrap:anywhere}.object-link:hover{text-decoration:underline}.workspace-empty{color:var(--muted);font-size:13px;line-height:1.7;padding:12px 0}.catalog-eyebrow{color:#4361bd;margin-bottom:8px}.catalog-filters{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:12px;margin-bottom:18px}.catalog-filters label{font-size:12px;font-weight:650;color:var(--muted)}.catalog-filters input,.catalog-filters select{display:block;width:100%;min-width:0;padding:11px;border:1px solid var(--line);border-radius:9px;background:#fafcff;margin-top:7px;color:var(--ink)}.catalog-actions,.detail-actions{display:flex;gap:8px;flex-wrap:wrap}.detail-actions{margin-top:16px}.favorite-button{border:1px solid var(--line);background:white;border-radius:8px;min-height:36px;min-width:36px;cursor:pointer;color:#53657e}.favorite-button[aria-pressed="true"]{color:#775300;background:#fff6d6;border-color:#ddc36e}.catalog-table td{vertical-align:middle}.catalog-table td small{display:block;color:var(--muted);margin-top:4px;overflow-wrap:anywhere}.catalog-table .object-link{font-size:13px}.skip-link{position:fixed;left:12px;top:-80px;z-index:100;background:#fff;color:#172235;padding:12px;border-radius:8px}.skip-link:focus{top:12px}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,[tabindex]:focus-visible{outline:3px solid #7297ff;outline-offset:3px}.metrics .metric{border-top:3px solid #cad6f6}.nav button.active{box-shadow:inset 3px 0 #83efd3}.health{white-space:nowrap}#catalogCount{font-size:13px;color:var(--muted)}@media(max-width:1100px){.workspace-grid{grid-template-columns:1fr}.catalog-filters{grid-template-columns:1fr 1fr}}@media(max-width:780px){.sidebar{padding:12px}.logo{padding-bottom:10px}.topbar{padding:10px 16px;height:auto;gap:8px}.health{font-size:11px}.hero{padding:25px}.catalog-filters{grid-template-columns:1fr}.panel-head{flex-wrap:wrap}.catalog-actions{width:100%}.metrics{grid-template-columns:1fr 1fr}.workspace-grid{margin:16px 0}.catalog-table{min-width:620px}.content{padding:14px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*:before,*:after{transition:none!important;scroll-behavior:auto!important}}@media print{.sidebar,.topbar,.hero-actions,.detail-actions,.catalog-actions,.skip-link{display:none!important}.app{display:block}.content{padding:0}.panel,.hero{box-shadow:none}.table-wrap{overflow:visible}.page:not(.active){display:none}}
'''

WORKSPACE_JS = r'''
// Personal shortcuts stay in this browser, scoped to this repository and path.
const workspaceKey='eaops:workspace:v1:'+JSON.stringify([EA.config?.repository?.url||EA.config?.name||'repository',location.pathname]);
let workspace={favorites:[],recent:[]};
try{
  const saved=JSON.parse(localStorage.getItem(workspaceKey)||'null');
  for(const key of ['favorites','recent'])
    if(Array.isArray(saved?.[key])) workspace[key]=[...new Set(saved[key].filter(id=>typeof id==='string'&&obj(id)))].slice(0,key==='recent'?8:500);
}catch{/* Storage may be unavailable or contain an obsolete draft. */}
function saveWorkspace(){
  try{localStorage.setItem(workspaceKey,JSON.stringify(workspace));}
  catch{toast('Browser storage unavailable. Shortcuts will last for this session.');}
}
function favoriteButton(id){return `<button class="favorite-button" data-favorite="${esc(id)}" aria-pressed="${workspace.favorites.includes(id)}" aria-label="Favorite ${esc(obj(id)?.name||id)}">${workspace.favorites.includes(id)?'★':'☆'}</button>`;}
function objectLink(o){return `<button class="object-link" data-open-object="${esc(o.id)}">${esc(o.name)}</button>`;}
function renderWorkspace(){
  const rows=ids=>ids.map(id=>obj(id)).filter(Boolean).slice(0,5).map(o=>`<div class="workspace-row"><div>${objectLink(o)}<div class="sub">${esc(props(o).owner||'Unassigned owner')}</div></div>${favoriteButton(o.id)}</div>`).join('');
  const unowned=objs.filter(o=>!String(props(o).owner||'').trim()).length;
  document.getElementById('dailyWorkspace').innerHTML=`<section class="panel"><h2>★ Your favorites</h2><div class="sub">Keep the architecture you work with close.</div>${rows(workspace.favorites)||'<p class="workspace-empty">Star an object in the catalog to keep it here. Favorites are private to this browser.</p>'}</section><section class="panel"><h2>Recently opened</h2><div class="sub">Pick up where you left off.</div>${rows(workspace.recent)||'<p class="workspace-empty">Open a catalog object to start your recent history.</p>'}</section><section class="panel"><h2>Review priorities</h2><div class="sub">A useful starting point for your next review.</div><div class="workspace-row"><button class="object-link" data-priority="unowned">Unassigned owners</button><b>${unowned}</b></div><div class="workspace-row"><button class="object-link" data-priority="critical">High / critical assets</button><b>${objs.filter(o=>['high','critical'].includes(props(o).criticality)).length}</b></div><div class="workspace-row"><button class="object-link" data-priority="quality">Governance findings</button><b>${(EA.issues||[]).length}</b></div></section>`;
}
function catalogMatches(){
  const q=document.getElementById('catalogSearch').value.trim().toLowerCase(),layer=document.getElementById('catalogLayer').value,owner=document.getElementById('catalogOwner').value,scope=document.getElementById('catalogScope').value;
  return objs.filter(o=>{
    const p=props(o),assigned=String(p.owner||'').trim();
    return (!q||[o.id,o.name,o.type,o.description,p.owner,p.lifecycle,p.criticality].join(' ').toLowerCase().includes(q))&&(!layer||layerOf(o)===layer)&&(!owner||(owner==='__unowned__'?!assigned:assigned===owner))&&(!scope||(scope==='favorites'?workspace.favorites.includes(o.id):['high','critical'].includes(p.criticality)));
  }).sort((a,b)=>String(a.name).localeCompare(String(b.name))||a.id.localeCompare(b.id));
}
function renderCatalog(){
  const matches=catalogMatches();
  document.getElementById('catalogCount').textContent=`${matches.length} of ${objs.length} objects`;
  document.getElementById('catalogResults').innerHTML=matches.length?`<div class="table-wrap"><table class="catalog-table"><thead><tr><th scope="col">Favorite</th><th scope="col">Object</th><th scope="col">Layer</th><th scope="col">Owner</th><th scope="col">Lifecycle</th><th scope="col">Criticality</th></tr></thead><tbody>${matches.map(o=>`<tr><td>${favoriteButton(o.id)}</td><td>${objectLink(o)}<small>${esc(o.id)} · ${esc(o.type)}</small></td><td>${esc(layerMeta(o).label)}</td><td>${esc(props(o).owner||'Unassigned')}</td><td>${esc(props(o).lifecycle||'—')}</td><td>${esc(props(o).criticality||'—')}</td></tr>`).join('')}</tbody></table></div>`:'<div class="empty"><h3>No matching objects</h3><p>Try a different search or reset the filters.</p></div>';
}
function resetCatalog(){for(const id of ['catalogSearch','catalogLayer','catalogOwner','catalogScope'])document.getElementById(id).value='';renderCatalog();}
// Neutralize spreadsheet formulas as well as quoting commas, quotes and newlines.
function csvCell(value){let s=String(value??'');if(/^[\s]*[=+@\-\t\r\n]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';}
function exportCatalog(){
  const rows=[['ID','Name','Type','Layer','Owner','Lifecycle','Criticality','Description'],...catalogMatches().map(o=>[o.id,o.name,o.type,layerMeta(o).label,props(o).owner,props(o).lifecycle,props(o).criticality,o.description])];
  const blob=new Blob(['\uFEFF'+rows.map(row=>row.map(csvCell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');
  a.href=url;a.download='ea-ops-catalog.csv';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);toast('Filtered catalog exported');
}
function navigateObject(id){
  if(!obj(id)){toast('This object is no longer in the model');return;}
  openAny(id);
  setRoute('object='+encodeURIComponent(id));
}
function setRoute(route){try{history.replaceState(null,'','#'+route);}catch{/* Some local-file browsers disallow history updates. */}}
const workspaceBaseShowPage=showPage;
showPage=function(name){workspaceBaseShowPage(name);if(name==='catalog')renderCatalog();if(name==='overview')renderWorkspace();document.querySelectorAll('.nav button').forEach(b=>{if(b.dataset.page===name)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});setRoute('page='+encodeURIComponent(name));};
const workspaceBaseDetailHero=detailHero;
detailHero=function(o){return workspaceBaseDetailHero(o)+`<div class="detail-actions">${favoriteButton(o.id)}<button class="soft" data-copy-object="${esc(o.id)}">Copy direct link</button><button class="soft" data-inspect-object="${esc(o.id)}">Explore dependencies →</button></div>`;};
function rememberObject(id){if(obj(id)){workspace.recent=[id,...workspace.recent.filter(x=>x!==id)].slice(0,8);saveWorkspace();renderWorkspace();setRoute('object='+encodeURIComponent(id));}}
const workspaceBaseOpenProcess=openProcess;
openProcess=function(id){workspaceBaseOpenProcess(id);rememberObject(id);};
const workspaceBaseOpenGeneric=openGeneric;
openGeneric=function(page,target,id){workspaceBaseOpenGeneric(page,target,id);rememberObject(id);};
// Existing process cards and relationship links use openAny too.
const workspaceBaseOpenAny=openAny;
openAny=function(id){workspaceBaseOpenAny(id);if(obj(id)&&!location.hash.startsWith('#object='))rememberObject(id);};
async function copyObjectLink(id){
  const url=new URL(location.href);url.hash='object='+encodeURIComponent(id);
  try{await navigator.clipboard.writeText(url.href);toast('Direct link copied');}
  catch{window.prompt('Copy this direct link:',url.href);}
}
document.addEventListener('click',event=>{
  const b=event.target.closest('button');if(!b)return;
  if(b.hasAttribute('data-favorite')){
    const id=b.dataset.favorite;if(!obj(id))return;
    workspace.favorites=workspace.favorites.includes(id)?workspace.favorites.filter(x=>x!==id):[...workspace.favorites,id];saveWorkspace();renderWorkspace();renderCatalog();
    document.querySelectorAll('[data-favorite]').forEach(el=>{if(el.dataset.favorite===id){el.setAttribute('aria-pressed',String(workspace.favorites.includes(id)));el.textContent=workspace.favorites.includes(id)?'★':'☆';}});
  }
  if(b.hasAttribute('data-open-object'))navigateObject(b.dataset.openObject);
  if(b.hasAttribute('data-copy-object'))copyObjectLink(b.dataset.copyObject);
  if(b.hasAttribute('data-inspect-object')){showPage('explorer');document.getElementById('explorerObject').value=b.dataset.inspectObject;renderExplorer();}
  if(b.dataset.priority){if(b.dataset.priority==='quality')return showPage('quality');resetCatalog();document.getElementById(b.dataset.priority==='unowned'?'catalogOwner':'catalogScope').value=b.dataset.priority==='unowned'?'__unowned__':'critical';showPage('catalog');}
});
for(const [key,meta] of Object.entries(LAYERS)){const option=new Option(meta.label,key);document.getElementById('catalogLayer').add(option);}
for(const owner of [...new Set(objs.map(o=>String(props(o).owner||'').trim()).filter(Boolean))].sort())document.getElementById('catalogOwner').add(new Option(owner,owner));
for(const id of ['catalogSearch','catalogLayer','catalogOwner','catalogScope'])document.getElementById(id).addEventListener('input',renderCatalog);
document.getElementById('resetCatalog').addEventListener('click',resetCatalog);
document.getElementById('exportCatalog').addEventListener('click',exportCatalog);
globalSearch=function(q){resetCatalog();document.getElementById('catalogSearch').value=q;showPage('catalog');};
document.addEventListener('keydown',event=>{
  if(event.key==='/'&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!event.target.closest('input,textarea,select,[contenteditable="true"]')){event.preventDefault();document.getElementById('globalSearch').focus();}
  if(event.key==='Escape'&&event.target.id==='globalSearch'){event.target.value='';event.target.blur();}
});
function restoreWorkspaceRoute(){
  const params=new URLSearchParams(location.hash.slice(1)),id=params.get('object'),page=params.get('page');
  if(id){if(obj(id))navigateObject(id);else{showPage('catalog');toast('Linked object was not found in this model');}}
  else if(page&&document.getElementById('page-'+page))showPage(page);
}
window.addEventListener('hashchange',restoreWorkspaceRoute);
renderWorkspace();renderCatalog();restoreWorkspaceRoute();
if(!(EA.metrics?.errors)&&EA.metrics?.warnings){document.getElementById('healthText').textContent=EA.metrics.warnings+' warning(s)';document.getElementById('healthDot').style.background='#b76e00';document.getElementById('healthDot').style.boxShadow='0 0 0 4px #fff1d6';}
const navIcons={overview:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',catalog:'M4 4h16v16H4z M8 8h8 M8 12h8 M8 16h5',processes:'M4 5v10h12 M12 11l4 4-4 4',data:'M12 3l9 9-9 9-9-9z',applications:'M4 4h16v16H4z M4 10h16 M10 4v16',technology:'M12 2l9 5v10l-9 5-9-5V7z',strategy:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8',motivation:'M9 18h6 M9 21h6 M8 14a6 6 0 1 1 8 0l-1 2H9z',implementation:'M4 7h15 M15 3l4 4-4 4 M20 17H5 M9 13l-4 4 4 4',explorer:'M5 5h4v4H5z M15 15h4v4h-4z M7 9v8h8 M9 7h8v8',notation:'M4 5h16 M8 5v15 M16 5v15 M4 15h16',quality:'M4 12l5 5L20 6'};
document.querySelectorAll('.nav button').forEach(button=>{const node=button.firstChild;if(node?.nodeType===Node.TEXT_NODE)node.textContent=node.textContent.replace(/^\S+\s*/, '');const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width','18');svg.setAttribute('height','18');svg.setAttribute('aria-hidden','true');svg.style.flexShrink='0';svg.innerHTML=`<path d="${navIcons[button.dataset.page]||navIcons.catalog}" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>`;button.prepend(svg);});
// Label legacy controls and make existing clickable cards operable by keyboard.
for(const input of document.querySelectorAll('input,select'))if(!input.labels?.length&&!input.getAttribute('aria-label'))input.setAttribute('aria-label',input.placeholder||input.id.replace(/([A-Z])/g,' $1'));
function accessibleCards(){document.querySelectorAll('.arch-card,.item,.step').forEach(el=>{el.tabIndex=0;el.setAttribute('role','button');});}
new MutationObserver(accessibleCards).observe(document.querySelector('.content'),{childList:true,subtree:true});accessibleCards();
document.addEventListener('keydown',e=>{if((e.key==='Enter'||e.key===' ')&&e.target.matches('.arch-card,.item,.step')){e.preventDefault();e.target.click();}});
'''
