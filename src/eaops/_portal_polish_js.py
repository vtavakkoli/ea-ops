PORTAL_POLISH_JS = r'''
// EA-Ops diagram presentation refinements. Kept separate from the core renderer so
// notation/layout behavior can evolve without coupling the repository UI to one view.
const EAOPS_LANE_GUTTER = 165;

const _eaopsBaseDims = dims;
dims = function(n){
  const d = _eaopsBaseDims(n);
  if(/Event$/.test(n?.type||'')) return {w:220,h:64};
  return d;
};

const _eaopsBaseEventAdornment = eventAdornment;
eventAdornment = function(n,x,y){
  // shapeMarkup passes the legacy right-side anchor. Reposition presentation
  // adornments into the top-right corner, leaving the semantic label unobstructed.
  const d=dims(n);
  return _eaopsBaseEventAdornment(n,x+30,y-d.h/2+17);
};

function eaopsShiftAutoLayout(base){
  const shift=135;
  const pos={};
  for(const [id,p] of Object.entries(base.pos||{})) pos[id]=[p[0]+shift,p[1]];
  return {...base,pos,W:(base.W||1100)+shift};
}

const _eaopsBaseAutoProcessLayout = autoProcessLayout;
autoProcessLayout = function(nodes){ return eaopsShiftAutoLayout(_eaopsBaseAutoProcessLayout(nodes)); };
const _eaopsBaseAutoLayerLayout = autoLayerLayout;
autoLayerLayout = function(nodes){ return eaopsShiftAutoLayout(_eaopsBaseAutoLayerLayout(nodes)); };

const _eaopsBaseDrawDiagram = drawDiagram;
drawDiagram = function(){
  _eaopsBaseDrawDiagram();
  const st=diagramState;
  if(!st) return;
  const host=document.getElementById(st.containerId);
  const svg=host?.querySelector('svg');
  if(!svg) return;
  const ns='http://www.w3.org/2000/svg';
  const height=svg.viewBox?.baseVal?.height||700;

  // Dedicated lane-title gutter: architecture content no longer competes with
  // BUSINESS / APPLICATION / TECHNOLOGY / MOTIVATION labels.
  const gutter=document.createElementNS(ns,'rect');
  gutter.setAttribute('x','0');
  gutter.setAttribute('y','0');
  gutter.setAttribute('width',String(EAOPS_LANE_GUTTER-8));
  gutter.setAttribute('height',String(height));
  gutter.setAttribute('fill','#f4f7fb');
  gutter.setAttribute('pointer-events','none');
  svg.insertBefore(gutter,svg.children[1]||null);

  const divider=document.createElementNS(ns,'line');
  divider.setAttribute('x1',String(EAOPS_LANE_GUTTER-8));
  divider.setAttribute('x2',String(EAOPS_LANE_GUTTER-8));
  divider.setAttribute('y1','0');
  divider.setAttribute('y2',String(height));
  divider.setAttribute('stroke','#d7e0eb');
  divider.setAttribute('pointer-events','none');
  svg.insertBefore(divider,svg.children[2]||null);

  const laneNames=new Set((st.base?.lanes||[]).map(([label])=>String(label).toUpperCase()));
  svg.querySelectorAll('line').forEach(line=>{
    if(line.getAttribute('x1')==='88' && line.getAttribute('y1')===line.getAttribute('y2')){
      line.setAttribute('x1',String(EAOPS_LANE_GUTTER));
    }
  });
  svg.querySelectorAll('text').forEach(text=>{
    if(laneNames.has((text.textContent||'').trim().toUpperCase())){
      text.setAttribute('x',String((EAOPS_LANE_GUTTER-8)/2));
      text.setAttribute('text-anchor','middle');
      text.setAttribute('font-size','10');
      text.setAttribute('fill','#7d8da3');
    }
  });

  // The ArchiMate event shape has a concave left edge. Move its semantic label
  // slightly right into the visual center while keeping its optional event-kind
  // icon in the top-right corner.
  for(const n of st.nodes||[]){
    if(!/Event$/.test(n.type||'')) continue;
    const group=[...svg.querySelectorAll('.node')].find(g=>g.dataset.id===n.id);
    if(!group) continue;
    group.querySelectorAll('text[font-weight="760"]').forEach(label=>{
      const x=Number(label.getAttribute('x'));
      if(Number.isFinite(x)) label.setAttribute('x',String(x+13));
    });
  }
};
'''
