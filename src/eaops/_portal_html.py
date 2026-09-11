PORTAL_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
  <div class="logo"><div class="mark">EA</div><div class="brand">EA-Ops<small>Architecture Repository</small></div></div>
  <div class="nav-title">Explore</div>
  <div class="nav">
    <button data-page="overview" class="active">◫ Overview</button>
    <button data-page="processes">↳ Processes <span class="count" id="navProcessCount"></span></button>
    <button data-page="data">◇ Information <span class="count" id="navDataCount"></span></button>
    <button data-page="applications">▦ Applications <span class="count" id="navAppCount"></span></button>
    <button data-page="technology">⬡ Technology <span class="count" id="navTechCount"></span></button>
    <button data-page="strategy">◎ Strategy</button>
    <button data-page="motivation">◉ Motivation</button>
    <button data-page="implementation">⇢ Implementation</button>
    <button data-page="explorer">⌘ Explorer</button>
    <button data-page="notation">⌗ Notation</button>
    <button data-page="quality">✓ Governance</button>
  </div>
  <div class="nav-title">Repository</div>
  <div class="repo-meta">Model: <b id="repoName"></b><br>Metamodel: <span id="metamodelName"></span><br>Views: <span id="viewCount"></span><br>Layout: Git + browser draft</div>
</aside>
<main class="main">
<div class="topbar"><div class="search"><input id="globalSearch" placeholder="Search architecture objects…"></div><div class="health"><span class="dot" id="healthDot"></span><span id="healthText">Model valid</span></div></div>
<div class="content">
<section id="page-overview" class="page active">
  <div class="hero"><div class="eyebrow">Enterprise architecture as code</div><h1 id="heroTitle"></h1><p>Explore an ArchiMate-aware repository with semantic notation, interactive diagrams, draggable Git-persisted layouts, architecture catalogs, relationship semantics and CI-backed governance.</p></div>
  <div class="metrics" id="metrics"></div>
  <div class="two"><div class="panel"><div class="panel-head"><div><h2>Business journey</h2><div class="sub">Processes and events ordered from Triggering relationships.</div></div><button class="soft" onclick="showPage('processes')">Open process repository</button></div><div class="flow-strip" id="overviewProcessFlow"></div></div><div class="panel"><div class="panel-head"><div><h2>Architecture coverage</h2><div class="sub">Elements by ArchiMate layer.</div></div></div><div id="layerBars"></div></div></div>
</section>
<section id="page-processes" class="page"><div class="section-title"><h1>Process repository</h1><p>Business behavior, events, responsibilities, application support, information and document representations in one governed process view.</p></div><div class="catalog-layout"><div class="list-panel"><div class="list-toolbar"><input id="processSearch" placeholder="Find a process…"><select id="processCriticality"><option value="">All criticalities</option><option>critical</option><option>high</option><option>medium</option><option>low</option></select></div><div class="list" id="processList"></div></div><div class="detail" id="processDetail"></div></div></section>
<section id="page-data" class="page"><div class="section-title"><h1>Information repository</h1><p>Business objects, data objects, contracts, representations and artifacts, including process usage, ownership, classification and realizations.</p></div><div class="filterbar"><input id="dataSearch" placeholder="Search information assets…"></div><div class="data-grid" id="dataGrid"></div><div id="dataDetail" class="detail spaced"></div></section>
<section id="page-applications" class="page"><div class="section-title"><h1>Application architecture</h1><p>Components, collaborations, interfaces, behavior, events, services and data objects.</p></div><div class="filterbar"><input id="appSearch" placeholder="Search application elements…"></div><div id="applicationGrid" class="card-grid"></div><div id="applicationDetail" class="detail spaced"></div></section>
<section id="page-technology" class="page"><div class="section-title"><h1>Technology & physical architecture</h1><p>Nodes, devices, system software, technology behavior, networks, artifacts and physical elements.</p></div><div class="filterbar"><input id="techSearch" placeholder="Search technology…"></div><div id="technologyGrid" class="card-grid"></div><div id="technologyDetail" class="detail spaced"></div></section>
<section id="page-strategy" class="page"><div class="section-title"><h1>Strategy</h1><p>Resources, capabilities, value streams and courses of action.</p></div><div id="strategyGrid" class="card-grid"></div><div id="strategyDetail" class="detail spaced"></div></section>
<section id="page-motivation" class="page"><div class="section-title"><h1>Motivation</h1><p>Stakeholders, drivers, assessments, goals, outcomes, principles, requirements, constraints, meaning and value.</p></div><div id="motivationGrid" class="card-grid"></div><div id="motivationDetail" class="detail spaced"></div></section>
<section id="page-implementation" class="page"><div class="section-title"><h1>Implementation & migration</h1><p>Work packages, deliverables, implementation events, plateaus and gaps.</p></div><div id="implementationGrid" class="card-grid"></div><div id="implementationDetail" class="detail spaced"></div></section>
<section id="page-explorer" class="page"><div class="section-title"><h1>Architecture explorer</h1><p>Inspect any object in context and navigate across semantic relationships.</p></div><div class="explorer-controls"><select id="explorerObject"></select><select id="explorerDepth"><option value="1">1 hop</option><option value="2" selected>2 hops</option><option value="3">3 hops</option></select></div><div class="panel"><div id="explorerDiagram" class="diagram"></div></div></section>
<section id="page-notation" class="page"><div class="section-title"><h1>ArchiMate notation library</h1><p>EA-Ops renders element and relationship notation from the semantic model type. Optional event icons are EA-Ops presentation adornments; the underlying element remains an ArchiMate event.</p></div><div id="notationLibrary"></div><div class="notation-group"><h2>Relationships</h2><div id="relationshipGallery" class="relationship-gallery"></div></div></section>
<section id="page-quality" class="page"><div class="section-title"><h1>Governance & quality</h1><p>The same deterministic checks shown here run in CI and pull requests.</p></div><div class="metrics" id="qualityMetrics"></div><div class="panel"><div class="panel-head"><div><h2>Validation findings</h2><div class="sub">Errors block the architecture gate; warnings remain visible for review.</div></div></div><div id="issues"></div></div></section>
</div>
</main>
</div>
<div class="toast" id="toast"></div>
<script>const EA=__DATA__;</script>
<script>__JS__</script>
</body>
</html>'''
