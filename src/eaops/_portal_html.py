PORTAL_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#0b1730">
<meta name="application-name" content="EA-Ops">
<meta name="description" content="EA-Ops interactive Enterprise Architecture as Code portal with ArchiMate notation, governed views, architecture catalogs, reports, and Git-native layout editing.">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta property="og:type" content="website">
<meta property="og:title" content="EA-Ops Interactive Architecture Portal">
<meta property="og:description" content="Browse Enterprise Architecture as Code with ArchiMate notation, interactive diagrams, governance, and Git-native layouts.">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2064%2064%22%3E%3Crect%20width%3D%2264%22%20height%3D%2264%22%20rx%3D%2216%22%20fill%3D%22%23101e38%22%2F%3E%3Cpath%20d%3D%22M16%2019h32M16%2032h32M16%2045h32M22%2019v26m20-26v26%22%20stroke%3D%22%237297ff%22%20stroke-width%3D%223%22%2F%3E%3Crect%20x%3D%2211%22%20y%3D%2212%22%20width%3D%2222%22%20height%3D%2214%22%20rx%3D%224%22%20fill%3D%22%2396b2ff%22%2F%3E%3Crect%20x%3D%2231%22%20y%3D%2225%22%20width%3D%2222%22%20height%3D%2214%22%20rx%3D%224%22%20fill%3D%22%235de0c5%22%2F%3E%3Crect%20x%3D%2211%22%20y%3D%2238%22%20width%3D%2222%22%20height%3D%2214%22%20rx%3D%224%22%20fill%3D%22%23fff%22%2F%3E%3C%2Fsvg%3E">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="app">
<aside class="sidebar">
  <div class="logo"><div class="mark" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#101e38"/><path d="M16 19h32M16 32h32M16 45h32M22 19v26m20-26v26" stroke="#7297ff" stroke-width="3"/><rect x="11" y="12" width="22" height="14" rx="4" fill="#96b2ff"/><rect x="31" y="25" width="22" height="14" rx="4" fill="#5de0c5"/><rect x="11" y="38" width="22" height="14" rx="4" fill="#fff"/></svg></div><div class="brand">EA-Ops<small>Architecture, connected</small></div></div>
  <div class="nav-title">Explore</div>
  <div class="nav">
    <button data-page="overview" class="active">◫ Overview</button>
    <button data-page="catalog">▤ Catalog</button>
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
<main class="main" id="main" tabindex="-1">
<div class="topbar"><div class="search"><input id="globalSearch" aria-label="Search all architecture objects" placeholder="Search names, owners, IDs… ( / )"></div><div class="health"><span class="dot" id="healthDot"></span><span id="healthText">Model valid</span></div></div>
<div class="content">
<section id="page-overview" class="page active">
  <div class="hero"><div class="eyebrow">Enterprise architecture as code</div><h1 id="heroTitle"></h1><p>Your architecture. A clearer next step. Find the right system, understand its connections, and turn decisions into reviewed changes.</p><div class="hero-actions"><button class="primary-action" onclick="showPage('catalog')">Explore the catalog →</button><button class="secondary-action" onclick="showPage('quality')">Review governance</button></div></div>
  <div class="metrics" id="metrics"></div>
  <div id="dailyWorkspace" class="workspace-grid"></div>
  <div class="two"><div class="panel"><div class="panel-head"><div><h2>Business journey</h2><div class="sub">Processes and events ordered from Triggering relationships.</div></div><button class="soft" onclick="showPage('processes')">Open process repository</button></div><div class="flow-strip" id="overviewProcessFlow"></div></div><div class="panel"><div class="panel-head"><div><h2>Architecture coverage</h2><div class="sub">Elements by ArchiMate layer.</div></div></div><div id="layerBars"></div></div></div>
</section>
<section id="page-catalog" class="page"><div class="section-title"><div class="eyebrow catalog-eyebrow">Your daily workspace</div><h1>Architecture catalog</h1><p>Find an owner, inspect dependencies, or build a shortlist for your next review.</p></div><div class="panel"><div class="catalog-filters"><label>Search<input id="catalogSearch" type="search" placeholder="Name, ID, description, owner…"></label><label>Layer<select id="catalogLayer"><option value="">All layers</option></select></label><label>Owner<select id="catalogOwner"><option value="">All owners</option><option value="__unowned__">Unassigned</option></select></label><label>Show<select id="catalogScope"><option value="">All objects</option><option value="favorites">Favorites</option><option value="critical">High / critical</option></select></label></div><div class="panel-head"><p id="catalogCount" role="status"></p><div class="catalog-actions"><button class="soft" id="resetCatalog">Reset filters</button><button class="soft" id="exportCatalog">Export CSV</button></div></div><div id="catalogResults"></div></div></section>
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
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>const EA=__DATA__;</script>
<script>__JS__</script>
</body>
</html>'''
