import os
import uuid
import subprocess
from functools import wraps
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
from database import supabase

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# ── Configuration & Paths ───────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf', 'docx', 'doc', 'mp4', 'webm', 'ogg'}
POLICIES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'policies')
PROJECTS_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'projects')
KNOWLEDGE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'knowledge')
BROCHURES_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'brochures')
LIVELIHOOD_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'livelihood')
COMMITTEE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'committee')
ORG_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', 'org')

# ── Site Config ───────────────────────────────────────────────────────────────
def load_site_config():
    default = {
        'policies': {'start_year': 2002, 'current_year': datetime.now().year},
        'reports': {'years': ['2024', '2023', '2022', '2021', '2020']},
        'scraper_schedule': {"enabled": False, "hour": "2", "minute": "0"}
    }
    try:
        response = supabase.table('site_config').select('config').eq('id', 'singleton').execute()
        if response.data:
            raw = response.data[0].get('config', {})
            merged = default.copy()
            merged.update(raw)
            return merged
    except Exception:
        pass
    return default

def save_site_config(config):
    supabase.table('site_config').upsert({'id': 'singleton', 'config': config}).execute()

# ── Helpers ────────────────────────────────────────────────────────────────────
def log_tracking(corner, entry_type, description, technical_officer=None):
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
    supabase.table('tracking_matrix').insert(entry).execute()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder_path, prefix="p"):
    if file and file.filename and allowed_file(file.filename):
        os.makedirs(folder_path, exist_ok=True)
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{prefix}_{str(uuid.uuid4())[:8]}.{ext}"
        file.save(os.path.join(folder_path, filename))
        parts = folder_path.replace('\\', '/').split('/')
        if 'static' in parts:
            static_idx = parts.index('static')
            return '/'.join(parts[static_idx+1:]) + '/' + filename
    return None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

# ── Public API ─────────────────────────────────────────────────────────────────
@admin_bp.route('/api/events')
def api_events():
    response = supabase.table('events').select('*').order('date').execute()
    return jsonify(response.data)

# ── Auth ──────────────────────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'gad2026')
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin.dashboard'))
        else:
            error = 'Invalid username or password.'
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

# ── Dashboard ─────────────────────────────────────────────────────────────────
@admin_bp.route('/')
@login_required
def dashboard():
    response = supabase.table('events').select('*').execute()
    events = response.data
    today = date.today().isoformat()
    current_month = date.today().strftime('%Y-%m')
    stats = {
        'total': len(events),
        'upcoming': sum(1 for e in events if e['date'] >= today),
        'this_month': sum(1 for e in events if e['date'].startswith(current_month)),
        'categories': len(set(e['category'] for e in events)),
    }
    upcoming = sorted([e for e in events if e['date'] >= today], key=lambda x: x['date'])[:5]
    return render_template('admin/dashboard.html', stats=stats, upcoming=upcoming)

# ── Features Management ───────────────────────────────────────────────────────
@admin_bp.route('/features')
@login_required
def features():
    site_config = load_site_config()
    schedule_config = site_config.get('scraper_schedule', {"enabled": False, "hour": "2", "minute": "0"})
    
    carousel_response = supabase.table('carousel').select('url').order('display_order').execute()
    carousel_images = [item['url'] for item in carousel_response.data]
    
    return render_template('admin/features.html', schedule=schedule_config, carousel_images=carousel_images, site_config=site_config)

@admin_bp.route('/save_carousel', methods=['POST'])
@login_required
def save_carousel():
    urls = request.form.getlist('urls[]')
    urls = [u.strip() for u in urls if u.strip()]
    try:
        # Delete existing carousel rows
        supabase.table('carousel').delete().neq('id', -1).execute()
        # Insert new rows
        if urls:
            records = [{'url': url, 'display_order': idx} for idx, url in enumerate(urls)]
            supabase.table('carousel').insert(records).execute()
        flash('Carousel images updated successfully.', 'success')
    except Exception as e:
        flash(f'Failed to update carousel: {e}', 'error')
    return redirect(url_for('admin.features'))

@admin_bp.route('/configure_scraper', methods=['POST'])
@login_required
def configure_scraper():
    enabled = request.form.get('enabled') == 'on'
    hour = request.form.get('hour', '2').strip()
    minute = request.form.get('minute', '0').strip()
    
    config = load_site_config()
    config['scraper_schedule'] = {"enabled": enabled, "hour": hour, "minute": minute}
    
    try:
        save_site_config(config)
        from app import setup_scheduler
        setup_scheduler()
        msg = f'Scraper schedule saved and enabled for {hour.zfill(2)}:{minute.zfill(2)} everyday.' if enabled else 'Scraper schedule saved and disabled.'
        flash(msg, 'success')
    except Exception as e:
        flash(f'Failed to save schedule: {e}', 'error')
    return redirect(url_for('admin.features'))

@admin_bp.route('/save_site_config', methods=['POST'], endpoint='save_site_config')
@login_required
def save_site_config_route():
    config = load_site_config()
    policies = config.get('policies', {})
    reports = config.get('reports', {})

    try:
        policies['start_year'] = int(request.form.get('policies_start_year', policies.get('start_year', 2002)))
        policies['current_year'] = int(request.form.get('policies_current_year', policies.get('current_year', datetime.now().year)))
        raw_years = request.form.get('reports_years', '')
        years = [y.strip() for y in raw_years.split(',') if y.strip()]
        if years: reports['years'] = years
        
        config['policies'] = policies
        config['reports'] = reports
        save_site_config(config)
        flash('Site configuration saved successfully.', 'success')
    except Exception as e:
        flash(f'Failed to save site settings: {e}', 'error')
    return redirect(url_for('admin.policies_settings'))

import sys

import threading

@admin_bp.route('/scrape_news', methods=['POST'])
@login_required
def scrape_news():
    # Use a more robust lock path for Windows/Production
    lock_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scraper.lock')
    
    if os.path.exists(lock_file):
        # Stale lock check: if file is older than 10 minutes, ignore it
        file_time = os.path.getmtime(lock_file)
        if (datetime.now().timestamp() - file_time) > 600:
            os.remove(lock_file)
        else:
            flash('A news scraper is already running in the background. Please wait for it to finish.', 'warning')
            return redirect(url_for('admin.features'))

    def run_async_scraper(python_exe, script, lock_path):
        try:
            # Create lock file
            os.makedirs(os.path.dirname(lock_path), exist_ok=True)
            with open(lock_path, 'w') as f:
                f.write(str(os.getpid()))
            
            print(f"[THREAD] Starting news scraper background process...")
            # Use a longer timeout or no timeout for the background process
            subprocess.run([python_exe, script], capture_output=True, text=True)
            print(f"[THREAD] News scraper background process finished.")
        except Exception as e:
            print(f"[THREAD] Scraper background process failed: {e}")
        finally:
            # Always remove the lock
            if os.path.exists(lock_path):
                try:
                    os.remove(lock_path)
                except:
                    pass

    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'scrape_news.py')
        thread = threading.Thread(target=run_async_scraper, args=(sys.executable, script_path, lock_file))
        thread.daemon = True
        thread.start()
        
        flash('News scraper started in the background. This may take 3-5 minutes. Check logs for progress.', 'success')
    except Exception as e:
        flash(f'Failed to initiate scraper: {str(e)}', 'error')
        
    return redirect(url_for('admin.features'))

# ── Policies Management ───────────────────────────────────────────────────────
@admin_bp.route('/policies')
@login_required
def policies_settings():
    site_config = load_site_config()
    response = supabase.table('policies').select('*').execute()
    # Reconstruct the nested dict structure for the template
    policies_data = {}
    for entry in response.data:
        cat = entry.get('category')
        policies_data.setdefault(cat, []).append(entry)
    return render_template('admin/policies.html', site_config=site_config, policies=policies_data)

@admin_bp.route('/policies/add', methods=['POST'])
@login_required
def add_policy_entry():
    category = request.form.get('category', 'circulars')
    site_config = load_site_config()
    year_default = site_config.get('policies', {}).get('current_year', datetime.now().year)
    
    file_path = save_uploaded_file(request.files.get('policy_file'), POLICIES_UPLOAD_FOLDER, prefix="memo")
    if not file_path: file_path = request.form.get('file', '').strip() or '#'
    
    video_path = save_uploaded_file(request.files.get('video_file'), POLICIES_UPLOAD_FOLDER, prefix="vid")
    if not video_path: video_path = request.form.get('video_path', '').strip()

    entry = {
        'id': 'p' + str(uuid.uuid4())[:8],
        'category': category,
        'year': int(request.form.get('year', year_default)),
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'date': request.form.get('date', '').strip(),
        'status': request.form.get('status', 'Active').strip() or 'Active',
        'file': file_path,
        'url': request.form.get('url', '').strip(),
        'video_file': video_path,
        'video_url': request.form.get('video_url', '').strip()
    }
    supabase.table('policies').insert(entry).execute()
    log_tracking("Digital", "Policy", f"Added new policy: {entry['title']}")
    flash('Policy entry added.', 'success')
    return redirect(url_for('admin.policies_settings'))

@admin_bp.route('/policies/edit/<entry_id>', methods=['POST'])
@login_required
def edit_policy_entry(entry_id):
    existing = supabase.table('policies').select('*').eq('id', entry_id).execute()
    if not existing.data:
        flash('Policy entry not found.', 'error')
        return redirect(url_for('admin.policies_settings'))
    old = existing.data[0]

    file_path = save_uploaded_file(request.files.get('policy_file'), POLICIES_UPLOAD_FOLDER, prefix="memo") or old.get('file')
    video_path = save_uploaded_file(request.files.get('video_file'), POLICIES_UPLOAD_FOLDER, prefix="vid") or old.get('video_file')

    updated = {
        'category': request.form.get('category', old['category']),
        'year': int(request.form.get('year', old['year'])),
        'title': request.form.get('title', old['title']).strip(),
        'description': request.form.get('description', old.get('description', '')).strip(),
        'date': request.form.get('date', old.get('date', '')).strip(),
        'status': request.form.get('status', old.get('status', 'Active')).strip(),
        'file': file_path,
        'url': request.form.get('url', old.get('url', '')).strip(),
        'video_file': video_path,
        'video_url': request.form.get('video_url', old.get('video_url', '')).strip()
    }
    supabase.table('policies').update(updated).eq('id', entry_id).execute()
    log_tracking("Digital", "Policy", f"Updated policy: {updated['title']}")
    flash('Policy entry updated.', 'success')
    return redirect(url_for('admin.policies_settings'))

@admin_bp.route('/policies/delete/<entry_id>', methods=['POST'])
@login_required
def delete_policy_entry(entry_id):
    supabase.table('policies').delete().eq('id', entry_id).execute()
    log_tracking("Digital", "Policy", "Deleted a policy entry")
    flash('Policy entry deleted.', 'success')
    return redirect(url_for('admin.policies_settings'))

# ── Events Management ──────────────────────────────────────────────────────────
@admin_bp.route('/events')
@login_required
def events():
    response = supabase.table('events').select('*').order('date').execute()
    return render_template('admin/events.html', events=response.data)

@admin_bp.route('/events/add', methods=['POST'])
@login_required
def add_event():
    new_event = {
        'id': 'e' + str(uuid.uuid4())[:8],
        'date': request.form.get('date', '').strip(),
        'title': request.form.get('title', '').strip(),
        'category': request.form.get('category', 'community').strip(),
        'description': request.form.get('desc', '').strip(),
    }
    if new_event['date'] and new_event['title']:
        supabase.table('events').insert(new_event).execute()
        log_tracking("Digital", "Event", f"Added new event: {new_event['title']}")
        flash('Event added successfully.', 'success')
    else:
        flash('Title and date are required.', 'error')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/edit/<event_id>', methods=['POST'])
@login_required
def edit_event(event_id):
    updated = {
        'title': request.form.get('title', '').strip(),
        'date': request.form.get('date', '').strip(),
        'category': request.form.get('category', '').strip(),
        'description': request.form.get('desc', '').strip(),
    }
    supabase.table('events').update(updated).eq('id', event_id).execute()
    flash('Event updated.', 'success')
    return redirect(url_for('admin.events'))

@admin_bp.route('/events/delete/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    supabase.table('events').delete().eq('id', event_id).execute()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin.events'))

# ── Project Archives Management ───────────────────────────────────────────────
@admin_bp.route('/projects')
@login_required
def projects():
    response = supabase.table('projects').select('*').order('year', desc=True).execute()
    all_projects = response.data
    years = sorted(set(int(p.get('year')) for p in all_projects if p.get('year')), reverse=True)
    return render_template('admin/projects.html', projects=all_projects, years=years, total=len(all_projects))

@admin_bp.route('/projects/add', methods=['POST'])
@login_required
def add_project():
    image_path = save_uploaded_file(request.files.get('image'), PROJECTS_UPLOAD_FOLDER, prefix="proj")
    new_project = {
        'id': 'p' + str(uuid.uuid4())[:8],
        'year': int(request.form.get('year', datetime.now().year)),
        'title': request.form.get('title', '').strip(),
        'category': request.form.get('category', '').strip(),
        'description': request.form.get('description', '').strip(),
        'status': request.form.get('status', 'Ongoing').strip(),
        'image': image_path,
    }
    supabase.table('projects').insert(new_project).execute()
    log_tracking("Digital", "Project Archive", f"Added project: {new_project['title']}")
    flash('Project added successfully.', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/edit/<project_id>', methods=['POST'])
@login_required
def edit_project(project_id):
    existing = supabase.table('projects').select('*').eq('id', project_id).execute()
    if not existing.data: return redirect(url_for('admin.projects'))
    old = existing.data[0]
    
    image_path = save_uploaded_file(request.files.get('image'), PROJECTS_UPLOAD_FOLDER, prefix="proj") or old.get('image')
    updated = {
        'year': int(request.form.get('year', old['year'])),
        'title': request.form.get('title', old['title']).strip(),
        'category': request.form.get('category', old.get('category', '')).strip(),
        'description': request.form.get('description', old.get('description', '')).strip(),
        'status': request.form.get('status', old.get('status', 'Ongoing')).strip(),
        'image': image_path
    }
    supabase.table('projects').update(updated).eq('id', project_id).execute()
    flash('Project updated.', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/projects/delete/<project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    supabase.table('projects').delete().eq('id', project_id).execute()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin.projects'))

# ── Knowledge Products Management ───────────────────────────────────────────
@admin_bp.route('/knowledge')
@login_required
def knowledge():
    response = supabase.table('knowledge_products').select('*').order('created_at', desc=True).execute()
    return render_template('admin/knowledge.html', items=response.data)

@admin_bp.route('/knowledge/add', methods=['POST'])
@login_required
def add_knowledge_entry():
    image_path = save_uploaded_file(request.files.get('image'), KNOWLEDGE_UPLOAD_FOLDER, prefix="kp_img")
    file_path = save_uploaded_file(request.files.get('file'), KNOWLEDGE_UPLOAD_FOLDER, prefix="kp_file")
    
    new_item = {
        'id': 'kp' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'type': request.form.get('type', 'Material').strip(),
        'date': request.form.get('date', '').strip(),
        'image': image_path or request.form.get('image_url', ''),
        'file': file_path or request.form.get('file_url', '#'),
        'url': request.form.get('url', '').strip(),
        'action_text': request.form.get('action_text', 'View Document').strip()
    }
    supabase.table('knowledge_products').insert(new_item).execute()
    flash('Knowledge Product added.', 'success')
    return redirect(url_for('admin.knowledge'))

@admin_bp.route('/knowledge/delete/<item_id>', methods=['POST'])
@login_required
def delete_knowledge_entry(item_id):
    supabase.table('knowledge_products').delete().eq('id', item_id).execute()
    flash('Knowledge Product deleted.', 'success')
    return redirect(url_for('admin.knowledge'))

# ── Brochures Management ──────────────────────────────────────────────────
@admin_bp.route('/brochures')
@login_required
def brochures():
    response = supabase.table('brochures').select('*').execute()
    return render_template('admin/brochures.html', items=response.data)

@admin_bp.route('/brochures/add', methods=['POST'])
@login_required
def add_brochure():
    file_path = save_uploaded_file(request.files.get('file'), BROCHURES_UPLOAD_FOLDER, prefix="br")
    new_item = {
        'id': 'br' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'url': request.form.get('url', '').strip(),
        'file': file_path or request.form.get('file_url', '#')
    }
    supabase.table('brochures').insert(new_item).execute()
    flash('Brochure added.', 'success')
    return redirect(url_for('admin.brochures'))

@admin_bp.route('/brochures/delete/<item_id>', methods=['POST'])
@login_required
def delete_brochure(item_id):
    supabase.table('brochures').delete().eq('id', item_id).execute()
    flash('Brochure deleted.', 'success')
    return redirect(url_for('admin.brochures'))

# ── Livelihood Feeds Management ──────────────────────────────────────────
@admin_bp.route('/livelihood-feeds')
@login_required
def livelihood_feeds():
    response = supabase.table('livelihood_feeds').select('*').order('date', desc=True).execute()
    return render_template('admin/livelihood_feeds.html', items=response.data)

@admin_bp.route('/livelihood-feeds/add', methods=['POST'])
@login_required
def add_livelihood_feed():
    file_path = save_uploaded_file(request.files.get('file'), LIVELIHOOD_UPLOAD_FOLDER, prefix="lf")
    new_item = {
        'id': 'lf' + str(uuid.uuid4())[:8],
        'title': request.form.get('title', '').strip(),
        'description': request.form.get('description', '').strip(),
        'type': request.form.get('type', 'facebook').strip(),
        'url': request.form.get('url', '').strip(),
        'file': file_path,
        'date': request.form.get('date', '').strip() or date.today().isoformat()
    }
    supabase.table('livelihood_feeds').insert(new_item).execute()
    flash('Livelihood Feed added.', 'success')
    return redirect(url_for('admin.livelihood_feeds'))

@admin_bp.route('/livelihood-feeds/delete/<feed_id>', methods=['POST'])
@login_required
def delete_livelihood_feed(feed_id):
    supabase.table('livelihood_feeds').delete().eq('id', feed_id).execute()
    flash('Feed deleted.', 'success')
    return redirect(url_for('admin.livelihood_feeds'))

# ── GFPS Structure Management ─────────────────────────────────────────
@admin_bp.route('/org-structure', endpoint='org_structure')
@login_required
def gfps_structure():
    response = supabase.table('org_structure').select('*').eq('id', 'singleton').execute()
    data = response.data[0] if response.data else {}
    return render_template('admin/org_structure.html', data=data)

@admin_bp.route('/org-structure/update', methods=['POST'])
@login_required
def update_org_structure():
    response = supabase.table('org_structure').select('*').eq('id', 'singleton').execute()
    data = response.data[0] if response.data else {'id': 'singleton', 'components': []}
    
    chart = save_uploaded_file(request.files.get('chart_image'), ORG_UPLOAD_FOLDER, prefix="chart")
    if chart: data['chart_image'] = chart
    pdf = save_uploaded_file(request.files.get('pdf'), ORG_UPLOAD_FOLDER, prefix="pdf")
    if pdf: data['pdf_url'] = pdf
    manual = save_uploaded_file(request.files.get('manual'), ORG_UPLOAD_FOLDER, prefix="manual")
    if manual: data['manual_url'] = manual
    
    component_titles = request.form.getlist('component_titles[]')
    component_descs = request.form.getlist('component_descs[]')
    data['components'] = [{"title": t.strip(), "description": d.strip()} for t, d in zip(component_titles, component_descs) if t.strip() or d.strip()]
    
    supabase.table('org_structure').upsert(data).execute()
    flash('Organization structure updated.', 'success')
    return redirect(url_for('admin.org_structure'))

# ── GFPS Committee Management ─────────────────────────────────────────
@admin_bp.route('/committee', endpoint='committee')
@login_required
def gfps_committee():
    response = supabase.table('committee').select('*').execute()
    return render_template('admin/committee.html', members=response.data)

@admin_bp.route('/committee/add', methods=['POST'])
@login_required
def add_committee_member():
    image_path = save_uploaded_file(request.files.get('image'), COMMITTEE_UPLOAD_FOLDER, prefix="member")
    new_member = {
        'id': 'mem' + str(uuid.uuid4())[:8],
        'name': request.form.get('name', '').strip(),
        'role': request.form.get('role', 'Member').strip(),
        'position': request.form.get('position', '').strip(),
        'image': image_path
    }
    supabase.table('committee').insert(new_member).execute()
    flash('Member added.', 'success')
    return redirect(url_for('admin.committee'))

@admin_bp.route('/committee/delete/<member_id>', methods=['POST'])
@login_required
def delete_committee_member(member_id):
    supabase.table('committee').delete().eq('id', member_id).execute()
    flash('Member removed.', 'success')
    return redirect(url_for('admin.committee'))

# ── Tracking Matrix Management ─────────────────────────────────────────
@admin_bp.route('/tracking-matrix')
@login_required
def tracking_matrix():
    response = supabase.table('tracking_matrix').select('*').order('created_at', desc=True).execute()
    return render_template('admin/tracking_matrix.html', entries=response.data)

@admin_bp.route('/tracking-matrix/add', methods=['POST'])
@login_required
def add_tracking_matrix():
    # Helper to format dates and times for the tracking matrix
    def fmt_date(d_str):
        try: return datetime.strptime(d_str, '%Y-%m-%d').strftime('%B %d, %Y')
        except: return d_str
    def fmt_time(t_str):
        try:
            ts = datetime.strptime(t_str, '%H:%M')
            return f"{ts.strftime('%I').lstrip('0') or '12'}:{ts.strftime('%M %p')}"
        except: return t_str

    new_entry = {
        'id': 'trk' + str(uuid.uuid4())[:8],
        'corner': request.form.get('corner', 'Physical').strip(),
        'date': fmt_date(request.form.get('date', '').strip()),
        'time_started': fmt_time(request.form.get('time_started', '').strip()),
        'time_completed': fmt_time(request.form.get('time_completed', '').strip()),
        'type': request.form.get('type', 'Content').strip(),
        'description': request.form.get('description', '').strip(),
        'updates_posted': request.form.get('updates_posted', '').strip(),
        'technical_officer': request.form.get('technical_officer', session.get('admin_user', 'System')).strip()
    }
    supabase.table('tracking_matrix').insert(new_entry).execute()
    flash('Tracking entry added.', 'success')
    return redirect(url_for('admin.tracking_matrix'))
