import asyncio
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, HTMLResponse

from config import WEB_HOST, WEB_PORT

app = FastAPI(title="Discord Moderation Bot Web")

_start_time = datetime.utcnow()

@app.get("/health")
async def health() -> Dict[str, Any]:
	return {
		"status": "ok",
		"uptime_seconds": (datetime.utcnow() - _start_time).total_seconds(),
	}

@app.get("/metrics")
async def metrics() -> PlainTextResponse:
	uptime = int((datetime.utcnow() - _start_time).total_seconds())
	lines = [
		"# HELP app_uptime_seconds Application uptime in seconds",
		"# TYPE app_uptime_seconds counter",
		f"app_uptime_seconds {uptime}",
	]
	return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

@app.get("/", response_class=HTMLResponse)
async def root() -> str:
	return """
	<!doctype html>
	<html lang=\"en\">
	<head>
		<meta charset=\"utf-8\" />
		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
		<title>Discord Moderation Bot</title>
		<style>
			body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;margin:40px;color:#e6e6e6;background:#1e1f22}
			.card{max-width:720px;margin:auto;padding:24px;border-radius:12px;background:#2b2d31;box-shadow:0 6px 24px rgba(0,0,0,.2)}
			.hint{color:#9aa0a6}
			code{background:#1e1f22;padding:2px 6px;border-radius:6px}
			ul{line-height:1.9}
		</style>
	</head>
	<body>
		<div class=\"card\">
			<h1>🤖 Discord Moderation Bot</h1>
			<p class=\"hint\">Web service is running.</p>
			<ul>
				<li><strong>Health</strong>: <code>GET /health</code></li>
				<li><strong>Metrics</strong>: <code>GET /metrics</code></li>
			</ul>
		</div>
	</body>
	</html>
	"""

@app.get("/favicon.ico")
async def favicon() -> PlainTextResponse:
	# Minimal 204 to avoid 404 noise; add real icon later if desired
	return PlainTextResponse("", status_code=204)

async def serve() -> None:
	import uvicorn
	config = uvicorn.Config(app=app, host=WEB_HOST, port=WEB_PORT, log_level="info")
	server = uvicorn.Server(config)
	await server.serve()
