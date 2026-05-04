"""
Web Handlers for Dashboard and Auth.

@Architecture-Map: [WEB-ROUTES]
"""
from aiohttp import web
import aiohttp_jinja2
import hashlib
import hmac
import time
from urllib.parse import unquote

from src.core.config import TELEGRAM_BOT_TOKEN
from src.db.repo import SessionLocal
from src.bot.handlers.utils import get_or_create_user
from src.web.auth import create_jwt_token, decode_jwt_token

routes = web.RouteTableDef()

def check_telegram_auth(data: dict) -> bool:
    """Verifies the cryptographic hash received from Telegram Login Widget."""
    if 'hash' not in data:
        return False
        
    check_hash = data.pop('hash')
    
    # 1. Data-check-string is a concatenation of all received fields, sorted in alphabetical order
    data_check_array = []
    for key, value in sorted(data.items()):
        data_check_array.append(f"{key}={value}")
    data_check_string = "\n".join(data_check_array)
    
    # 2. Compute a secret key from the bot token
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode('utf-8')).digest()
    
    # 3. Create HMAC-SHA-256 signature
    hmac_signature = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # 4. Check if timestamp is too old (e.g. older than 24 hours to prevent replay attacks)
    auth_date = int(data.get('auth_date', 0))
    if time.time() - auth_date > 86400:
        return False
        
    return hmac.compare_digest(hmac_signature, check_hash)

@routes.get('/')
@aiohttp_jinja2.template('landing.html')
async def index_handler(request: web.Request):
    """The public landing page."""
    # Check if already logged in
    token = request.cookies.get('pulse_session')
    user_data = None
    if token:
        user_data = decode_jwt_token(token)
        if user_data:
            # Redirect to app if logged in
            raise web.HTTPFound('/app')
            
    bot_username = "pulse_monolith_bot" # Fallback, ideally we'd fetch this from the bot object if needed
    return {'bot_username': bot_username}

@routes.get('/auth/telegram')
async def auth_telegram_handler(request: web.Request):
    """Endpoint that Telegram redirects to after successful widget login."""
    data = dict(request.query)
    
    if not check_telegram_auth(data.copy()):
        return web.Response(text="Authentication Failed: Invalid Hash.", status=403)
        
    telegram_id = int(data.get('id', 0))
    first_name = data.get('first_name', 'Unknown')
    
    # Create or get user in DB
    with SessionLocal() as db:
        user = get_or_create_user(db, telegram_id)
        # Update user's name if we wanted to store it, but for now we just need the ID
        user_id = user.id
        
    # Generate JWT
    jwt_data = {
        "user_id": user_id,
        "telegram_id": telegram_id,
        "first_name": first_name
    }
    token = create_jwt_token(jwt_data)
    
    # Redirect to dashboard with cookie
    response = web.HTTPFound('/app')
    response.set_cookie('pulse_session', token, httponly=True, samesite='Lax', secure=True, max_age=7*24*3600)
    
    return response

@routes.get('/auth/logout')
async def logout_handler(request: web.Request):
    response = web.HTTPFound('/')
    response.del_cookie('pulse_session')
    return response

# --- Protected Routes ---
def require_auth(handler):
    """Decorator to protect dashboard routes."""
    async def wrapper(request: web.Request):
        token = request.cookies.get('pulse_session')
        if not token:
            raise web.HTTPFound('/')
            
        user_data = decode_jwt_token(token)
        if not user_data:
            raise web.HTTPFound('/')
            
        # Inject user data into request
        request['user'] = user_data
        return await handler(request)
    return wrapper

@routes.get('/app')
@require_auth
@aiohttp_jinja2.template('dashboard.html')
async def dashboard_handler(request: web.Request):
    user_data = request['user']
    
    with SessionLocal() as db:
        from src.db.models import Project, TimeLog
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Fetch Active Projects
        projects = db.query(Project).filter(Project.user_id == user_data['user_id'], Project.status == 'active').all()
        
        # Fetch total focus time
        total_logs = db.query(func.sum(TimeLog.duration_minutes)).filter(TimeLog.user_id == user_data['user_id']).scalar() or 0
        total_hours = round(total_logs / 60, 1)
        
    return {
        'user': user_data,
        'projects': projects,
        'total_hours': total_hours
    }
