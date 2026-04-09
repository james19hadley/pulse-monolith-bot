"""
Admin Dashboard for monitoring bot performance and basic stats via web interface.

@Architecture-Map: [CORE-ADMIN-DASH]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
from aiohttp import web
import base64
from src.core.config import ADMIN_LOGIN, ADMIN_PASSWORD
from src.db.repo import get_admin_metrics
import logging

def check_auth(request: web.Request) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return False
    
    try:
        encoded_creds = auth_header.split(" ")[1]
        decoded_creds = base64.b64decode(encoded_creds).decode("utf-8")
        login, password = decoded_creds.split(":", 1)
        return login == ADMIN_LOGIN and password == ADMIN_PASSWORD
    except Exception:
        return False

async def dashboard_handler(request: web.Request):
    if not check_auth(request):
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="Admin Dashboard"'},
            text="Unauthorized"
        )
    
    try:
        metrics = get_admin_metrics()
        
        # Read the last few lines of the log file
        log_lines = []
        try:
            with open("bot.log", "r") as f:
                # Get last 20 lines
                log_lines = f.readlines()[-20:]
        except Exception as e:
            log_lines = [f"Could not read logs: {e}"]
            
        logs_html = "".join([f"<div>{line}</div>" for line in log_lines])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pulse Monolith Admin</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
                .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #0066cc; margin: 10px 0; }}
                .metric-label {{ font-size: 14px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
                .logs-section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .logs-container {{ background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 4px; overflow-y: auto; max-height: 400px; font-family: monospace; font-size: 13px; line-height: 1.5; text-align: left; }}
                h1, h2 {{ margin-top: 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Pulse Monolith Admin Dashboard</h1>
                </div>
                
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-label">Total Users</div>
                        <div class="metric-value">{metrics.get('Total Users', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Active Focus Sessions</div>
                        <div class="metric-value">{metrics.get('Active Focus Sessions', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Tokens Used</div>
                        <div class="metric-value">{metrics.get('Total Tokens Used', 0)}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Total Focused Minutes Today</div>
                        <div class="metric-value">{metrics.get('Total Focused Minutes Today', 0)}</div>
                    </div>
                </div>
                
                <div class="logs-section">
                    <h2>Recent System Logs</h2>
                    <p style="font-size: 13px; color: #666;">Note: SafeLoggingMiddleware prevents PII or user text content from being stored. Only commands and message lengths are visible.</p>
                    <div class="logs-container">
                        {logs_html}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type="text/html")
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        return web.Response(text=f"Error loading dashboard: {str(e)}", status=500)

async def logs_handler(request: web.Request):
    if not check_auth(request):
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="Admin Logs"'},
            text="Unauthorized"
        )
    
    try:
        lines_param = request.query.get("lines", "50")
        try:
            num_lines = max(1, min(int(lines_param), 1000))
        except ValueError:
            num_lines = 50

        with open("bot.log", "r") as f:
            log_lines = f.readlines()
        
        return web.Response(text="".join(log_lines[-num_lines:]), content_type="text/plain")
    except Exception as e:
        return web.Response(text=f"Error reading logs: {e}", status=500)
