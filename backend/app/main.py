"""this1 — FastAPI entry point.

Wires routes + DB + middleware. Also serves branded landing page at `/`
and a branded custom Swagger UI at `/docs`.
"""
from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from . import ws as ws_module
from .db import init_db
from .middleware.defender import DefenderMiddleware
from .routes import dashboard, defender, honeypot, model_info, salaries, sim


_BRAND_HEAD = """
<link rel="icon" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><text y='52' font-size='52'>%F0%9F%9B%A1%EF%B8%8F</text></svg>"/>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Nunito:wght@800;900&display=swap" rel="stylesheet" />
"""

_BRAND_STYLE = """
:root { color: #121317; font-family: Inter, system-ui, sans-serif; }
.wm   { font-family: Nunito, system-ui, sans-serif; font-weight: 900; letter-spacing: -0.04em; line-height: 1; }
.wm .this { color: #1E5BEC; }
.wm .one  { color: #F57C00; }
.sub  { color: #5F6368; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; }
"""

LANDING_HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>this1 — backend</title>
  {_BRAND_HEAD}
  <style>
    {_BRAND_STYLE}
    html,body{{margin:0;background:#fff;min-height:100vh}}
    body{{display:flex;align-items:center;justify-content:center;
      background:
        radial-gradient(900px circle at 10% -5%, rgba(66,133,244,.07), transparent 55%),
        radial-gradient(700px circle at 110% 5%, rgba(234,67,53,.05), transparent 55%),
        #fff;}}
    .wrap{{text-align:center;padding:48px;max-width:880px}}
    .wm.hero{{font-size:120px}}
    .tag{{margin-top:14px}}
    .cards{{margin-top:44px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}
    .card{{background:#fff;border:1px solid #E8EAED;border-radius:14px;padding:18px;text-align:left;
      transition:transform .2s cubic-bezier(.2,.7,.3,1.2),box-shadow .2s,border-color .2s;
      text-decoration:none;color:inherit}}
    .card:hover{{transform:translateY(-3px);border-color:#DADCE0;box-shadow:0 8px 24px rgba(60,64,67,.08)}}
    .card .h{{font-weight:600;color:#121317}}
    .card .s{{color:#5F6368;font-size:13px;margin-top:4px}}
    .pill{{display:inline-block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
      color:#1A73E8;background:#E8F0FE;border-radius:999px;padding:4px 12px;margin-bottom:18px}}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="pill">Backend · :8000</div>
    <div class="wm hero"><span class="this">this</span><span class="one">1</span></div>
    <div class="sub tag">Adaptive bot defense · Levels.fyi</div>
    <div class="cards">
      <a class="card" href="/docs"><div class="h">API explorer (Swagger)</div><div class="s">Try every endpoint, inspect schemas.</div></a>
      <a class="card" href="/redoc"><div class="h">API reference (ReDoc)</div><div class="s">Read-only documentation.</div></a>
      <a class="card" href="/api/dashboard/summary"><div class="h">Dashboard summary JSON</div><div class="s">Counts of verdicts & actions.</div></a>
      <a class="card" href="/api/model/info"><div class="h">Trained model metrics</div><div class="s">Confusion matrix + feature importances.</div></a>
    </div>
  </div>
</body>
</html>"""


SWAGGER_HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>this1 — API</title>
  {_BRAND_HEAD}
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"/>
  <style>
    {_BRAND_STYLE}
    body{{margin:0;background:#fff}}
    .topbar{{display:flex;align-items:center;gap:20px;padding:16px 32px;border-bottom:1px solid #E8EAED;
      background:
        radial-gradient(700px circle at 10% -10%, rgba(66,133,244,.05), transparent 55%),
        radial-gradient(500px circle at 110% 0%, rgba(234,67,53,.04), transparent 55%),
        #fff;
      position:sticky;top:0;z-index:99;backdrop-filter:blur(8px)}}
    .topbar .left{{display:flex;align-items:center;gap:16px}}
    .wm.h{{font-size:38px}}
    .titlebar{{display:flex;flex-direction:column;gap:4px}}
    .titlebar .row1{{display:flex;align-items:baseline;gap:10px}}
    .titlebar .row1 h1{{margin:0;font-size:17px;font-weight:600;color:#121317}}
    .titlebar .badges{{display:flex;gap:6px}}
    .badge{{font-size:10px;font-weight:600;padding:2px 8px;border-radius:999px;letter-spacing:.04em}}
    .badge.ver  {{background:#F1F3F4;color:#3C4043}}
    .badge.oas  {{background:#E6F4EA;color:#137333}}
    .badge.json {{background:#E8F0FE;color:#1A73E8}}
    .links{{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}}
    .links a{{font-size:13px;color:#5F6368;text-decoration:none;padding:6px 14px;
      border:1px solid #DADCE0;border-radius:999px;transition:all .2s}}
    .links a:hover{{color:#1A73E8;border-color:#1A73E8;background:#E8F0FE}}
    /* Hide Swagger's redundant header — we put everything in our topbar */
    .swagger-ui .topbar{{display:none}}
    .swagger-ui .information-container,
    .swagger-ui .info{{display:none !important}}
    .swagger-ui .scheme-container{{box-shadow:none;background:transparent;padding:8px 0}}
    #swagger-ui{{max-width:1240px;margin:0 auto;padding:0 16px}}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="left">
      <div class="wm h"><span class="this">this</span><span class="one">1</span></div>
      <div class="titlebar">
        <div class="row1">
          <h1>Adaptive Bot Defense</h1>
          <div class="badges">
            <span class="badge ver">v0.1.0</span>
            <span class="badge oas">OAS 3.1</span>
            <a class="badge json" href="/openapi.json" style="text-decoration:none">openapi.json</a>
          </div>
        </div>
        <div class="sub">API Explorer</div>
      </div>
    </div>
    <div class="links">
      <a href="/">Backend home</a>
      <a href="http://localhost:3001" target="_blank">Dashboard</a>
      <a href="http://localhost:3000" target="_blank">Protected site</a>
      <a href="/redoc">ReDoc</a>
    </div>
  </div>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({{
      url: '/openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      docExpansion: 'list',
      defaultModelsExpandDepth: 0,
    }});
  </script>
</body>
</html>"""


REDOC_HTML = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>this1 — API reference</title>
  {_BRAND_HEAD}
  <style>
    {_BRAND_STYLE}
    body{{margin:0;background:#fff}}
    .topbar{{display:flex;align-items:center;gap:20px;padding:16px 32px;border-bottom:1px solid #E8EAED;
      background:
        radial-gradient(700px circle at 10% -10%, rgba(66,133,244,.05), transparent 55%),
        radial-gradient(500px circle at 110% 0%, rgba(234,67,53,.04), transparent 55%),
        #fff;
      position:sticky;top:0;z-index:99;backdrop-filter:blur(8px)}}
    .topbar .left{{display:flex;align-items:center;gap:16px}}
    .wm.h{{font-size:38px}}
    .titlebar{{display:flex;flex-direction:column;gap:4px}}
    .titlebar h1{{margin:0;font-size:17px;font-weight:600;color:#121317}}
    .links{{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}}
    .links a{{font-size:13px;color:#5F6368;text-decoration:none;padding:6px 14px;
      border:1px solid #DADCE0;border-radius:999px;transition:all .2s}}
    .links a:hover{{color:#1A73E8;border-color:#1A73E8;background:#E8F0FE}}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="left">
      <div class="wm h"><span class="this">this</span><span class="one">1</span></div>
      <div class="titlebar">
        <h1>API Reference</h1>
        <div class="sub">Read-only · powered by ReDoc</div>
      </div>
    </div>
    <div class="links">
      <a href="/">Backend home</a>
      <a href="/docs">Swagger</a>
      <a href="http://localhost:3001" target="_blank">Dashboard</a>
      <a href="http://localhost:3000" target="_blank">Protected site</a>
    </div>
  </div>
  <redoc spec-url="/openapi.json" hide-loading></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"></script>
</body>
</html>"""


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="this1 — Adaptive Bot Defense",
        description=(
            "**this1** — three-layer adaptive defense for Levels.fyi compensation data.\n\n"
            "* Layer 1 — invisible proof-of-work\n"
            "* Layer 2 — in-house CAPTCHA challenge\n"
            "* Layer 3 — confirmed bots get poisoned with decoy data\n\n"
            "Visit the [dashboard](http://localhost:3001) or the [site](http://localhost:3000)."
        ),
        version="0.1.0",
        docs_url=None,   # custom branded /docs below
        redoc_url=None,  # custom branded /redoc below
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(DefenderMiddleware)
    app.include_router(salaries.router)
    app.include_router(dashboard.router)
    app.include_router(defender.router)
    app.include_router(honeypot.router)
    app.include_router(model_info.router)
    app.include_router(sim.router)
    app.include_router(ws_module.router)

    @app.on_event("startup")
    async def _capture_loop() -> None:
        ws_module.set_loop(asyncio.get_running_loop())

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def root_page():
        return HTMLResponse(LANDING_HTML)

    @app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
    def docs_page():
        return HTMLResponse(SWAGGER_HTML)

    @app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
    def redoc_page():
        return HTMLResponse(REDOC_HTML)

    @app.get("/api/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
