import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Helper functions for database operations can be added here
def get_db():
    if not supabase:
        raise ConnectionError("Supabase client is not initialized. Please check your .env file.")
    return supabase

def log_tracking(corner, entry_type, description, technical_officer=None):
    from datetime import datetime
    import uuid
    
    if not technical_officer:
        try:
            from flask import session
            technical_officer = session.get('admin_user', 'System')
        except Exception:
            technical_officer = 'System'
            
    now = datetime.now()
    hour_12 = now.strftime('%I').lstrip('0') or '12'
    time_str = f"{hour_12}:{now.strftime('%M %p')}"
    date_str = now.strftime('%B %d, %Y')
    
    entry = {
        'id': 'trk' + str(uuid.uuid4())[:8],
        'corner': corner,
        'date': date_str,
        'time_started': time_str,
        'time_completed': time_str,
        'type': entry_type,
        'description': description,
        'updates_posted': f"{date_str}, {time_str}",
        'technical_officer': technical_officer
    }
    if supabase:
        supabase.table('tracking_matrix').insert(entry).execute()
