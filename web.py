import asyncio
from datetime import datetime
from typing import Any, Dict
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from config import WEB_HOST, WEB_PORT
from database import ModerationDB

app = FastAPI(title="Discord Moderation Bot Web")

_start_time = datetime.utcnow()
db = ModerationDB()

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

async def broadcast_stats_update():
    """Broadcast updated stats to all connected WebSocket clients"""
    stats = db.get_moderation_stats()
    message = json.dumps({
        'type': 'stats_update',
        'data': stats
    })
    await manager.broadcast(message)

# Set up database callback to broadcast updates
db.add_data_change_callback(lambda: asyncio.create_task(broadcast_stats_update()))

def get_moderation_stats() -> Dict[str, Any]:
    """Get current moderation statistics"""
    return db.get_moderation_stats()

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

@app.get("/api/stats")
async def get_stats() -> Dict[str, Any]:
    """API endpoint to get current moderation statistics"""
    return get_moderation_stats()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial stats
        stats = get_moderation_stats()
        await websocket.send_text(json.dumps({
            'type': 'stats_update',
            'data': stats
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_text(json.dumps({
                'type': 'pong',
                'data': data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
			.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:20px 0}
			.stat-card{background:#1e1f22;padding:20px;border-radius:8px;text-align:center}
			.stat-number{font-size:2.5em;font-weight:bold;color:#7289da;margin:10px 0}
			.stat-label{color:#9aa0a6;font-size:0.9em}
			.connection-status{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px}
			.connected{background:#43b581}
			.disconnected{background:#f04747}
			.refresh-btn{background:#7289da;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;margin:10px 0}
			.refresh-btn:hover{background:#5b6eae}
			.last-update{color:#9aa0a6;font-size:0.8em;text-align:center;margin-top:20px}
		</style>
	</head>
	<body>
		<div class=\"card\">
			<h1>🤖 Discord Moderation Bot</h1>
			<p class=\"hint\">Web service is running.</p>
			
			<div style="margin: 20px 0;">
				<span class="connection-status disconnected" id="connectionStatus"></span>
				<span id="connectionText">Disconnected</span>
				<button class="refresh-btn" onclick="connectWebSocket()">Connect</button>
				<button class="refresh-btn" onclick="manualRefresh()" style="margin-left: 10px;">Manual Refresh</button>
			</div>
			
			<div class="stats-grid" id="statsGrid">
				<div class="stat-card">
					<div class="stat-number" id="totalWarnings">-</div>
					<div class="stat-label">Total Warnings</div>
				</div>
				<div class="stat-card">
					<div class="stat-number" id="usersWarned">-</div>
					<div class="stat-label">Users Warned</div>
				</div>
				<div class="stat-card">
					<div class="stat-number" id="activeMutes">-</div>
					<div class="stat-label">Active Mutes</div>
				</div>
				<div class="stat-card">
					<div class="stat-number" id="totalBans">-</div>
					<div class="stat-label">Total Bans</div>
				</div>
				<div class="stat-card">
					<div class="stat-number" id="totalKicks">-</div>
					<div class="stat-label">Total Kicks</div>
				</div>
			</div>
			
			<div class="last-update" id="lastUpdate">Last updated: Never</div>
			
			<ul>
				<li><strong>Health</strong>: <code>GET /health</code></li>
				<li><strong>Metrics</strong>: <code>GET /metrics</code></li>
				<li><strong>Stats API</strong>: <code>GET /api/stats</code></li>
				<li><strong>WebSocket</strong>: <code>ws://localhost:8000/ws</code></li>
			</ul>
		</div>
		
		<script>
			let ws = null;
			let reconnectInterval = null;
			
			function updateStats(data) {
				document.getElementById('totalWarnings').textContent = data.total_warnings;
				document.getElementById('usersWarned').textContent = data.total_users_warned;
				document.getElementById('activeMutes').textContent = data.active_mutes;
				document.getElementById('totalBans').textContent = data.total_bans;
				document.getElementById('totalKicks').textContent = data.total_kicks;
				
				// Update last update time
				const now = new Date();
				document.getElementById('lastUpdate').textContent = `Last updated: ${now.toLocaleTimeString()}`;
			}
			
			function updateConnectionStatus(connected) {
				const statusEl = document.getElementById('connectionStatus');
				const textEl = document.getElementById('connectionText');
				
				if (connected) {
					statusEl.className = 'connection-status connected';
					textEl.textContent = 'Connected (Real-time)';
				} else {
					statusEl.className = 'connection-status disconnected';
					textEl.textContent = 'Disconnected';
				}
			}
			
			function connectWebSocket() {
				if (ws) {
					ws.close();
				}
				
				const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
				const wsUrl = protocol + '//' + window.location.host + '/ws';
				
				ws = new WebSocket(wsUrl);
				
				ws.onopen = function() {
					console.log('WebSocket connected');
					updateConnectionStatus(true);
					if (reconnectInterval) {
						clearInterval(reconnectInterval);
						reconnectInterval = null;
					}
				};
				
				ws.onmessage = function(event) {
					try {
						const message = JSON.parse(event.data);
						if (message.type === 'stats_update') {
							updateStats(message.data);
						}
					} catch (e) {
						console.error('Error parsing message:', e);
					}
				};
				
				ws.onclose = function() {
					console.log('WebSocket disconnected');
					updateConnectionStatus(false);
					
					// Auto-reconnect after 5 seconds
					if (!reconnectInterval) {
						reconnectInterval = setInterval(() => {
							if (ws.readyState === WebSocket.CLOSED) {
								connectWebSocket();
							}
						}, 5000);
					}
				};
				
				ws.onerror = function(error) {
					console.error('WebSocket error:', error);
					updateConnectionStatus(false);
				};
			}
			
			// Load initial stats
			async function loadInitialStats() {
				try {
					const response = await fetch('/api/stats');
					const data = await response.json();
					updateStats(data);
				} catch (e) {
					console.error('Error loading initial stats:', e);
				}
			}
			
			// Auto-connect on page load
			window.addEventListener('load', function() {
				loadInitialStats();
				connectWebSocket();
			});
		</script>
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
