import os
import math
from flask import Blueprint, render_template, request, jsonify, abort, current_app
from database import supabase

main_bp = Blueprint('main', __name__)

POSTS_PER_PAGE = 6

@main_bp.route('/')
def index():
    try:
        news_response = supabase.table('news').select('*').order('date', desc=True).limit(3).execute()
        latest_news = news_response.data
        carousel_response = supabase.table('carousel').select('url').order('display_order').execute()
        carousel_images = [item['url'] for item in carousel_response.data]
    except Exception:
        latest_news = []
        carousel_images = []
    return render_template('index.html', latest_news=latest_news, carousel_images=carousel_images)

@main_bp.route('/knowledge-products')
def knowledge_products():
    try:
        response = supabase.table('knowledge_products').select('*').order('created_at', desc=True).execute()
        products = response.data
    except Exception:
        products = []
    return render_template('knowledge-products.html', products=products)

@main_bp.route('/brochures')
def brochures():
    try:
        response = supabase.table('brochures').select('*').execute()
        brochures_list = response.data
    except Exception:
        brochures_list = []
    return render_template('brochures.html', brochures=brochures_list)

@main_bp.route('/livelihood-program')
def livelihood_program():
    try:
        response = supabase.table('livelihood_feeds').select('*').order('date', desc=True).execute()
        feeds = response.data
    except Exception:
        feeds = []
    return render_template('livelihood-program.html', feeds=feeds)

@main_bp.route('/about')
def about():
    return render_template('about/about.html')

@main_bp.route('/about/vision-mission')
def vision_mission():
    return render_template('about/vision-mission.html')

@main_bp.route('/about/org-structure')
def org_structure():
    try:
        response = supabase.table('org_structure').select('*').eq('id', 'singleton').execute()
        data = response.data[0] if response.data else {}
    except Exception:
        data = {}
    return render_template('about/org-structure.html', data=data)

@main_bp.route('/about/gad-committee')
def gad_committee():
    try:
        response = supabase.table('committee').select('*').execute()
        members = response.data
    except Exception:
        members = []
    return render_template('about/gad-committee.html', members=members)

@main_bp.route('/about/contact')
def contact():
    return render_template('about/contact.html')

@main_bp.route('/news')
def news_hub():
    page = request.args.get('page', 1, type=int)
    try:
        count_response = supabase.table('news').select('id', count='exact').execute()
        total_items = count_response.count if count_response.count is not None else 0
        total_pages = max(1, math.ceil(total_items / POSTS_PER_PAGE))
        page = max(1, min(page, total_pages))

        start = (page - 1) * POSTS_PER_PAGE
        news_response = supabase.table('news').select('*').order('date', desc=True).range(start, start + POSTS_PER_PAGE - 1).execute()
        news_items = news_response.data
    except Exception:
        news_items = []
        total_pages = 1

    return render_template(
        'news/news.html',
        news_items=news_items,
        page=page,
        total_pages=total_pages,
    )

@main_bp.route('/news/<news_id>')
def news_detail(news_id):
    try:
        response = supabase.table('news').select('*').eq('id', news_id).execute()
        if not response.data:
            abort(404)
        article = response.data[0]
    except Exception:
        abort(404)
    return render_template('news/news-detail.html', article=article)

# Mock searchable content remains for now, could be dynamic in future
searchable_content = [
    {'title': 'Annual GAD Plan and Budget', 'url': 'policies.reports', 'category': 'Reports'},
    {'title': 'GAD Focal Point System Structure', 'url': 'main.org_structure', 'category': 'About'},
    {'title': 'Gender Fair Language Circular', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'circulars'},
    {'title': 'Resolutions and Council Decrees', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'resolutions'},
    {'title': 'Memoranda and Internal Directives', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'memoranda'},
    {'title': 'Executive Orders and Designations', 'url': 'policies.policies_hub', 'category': 'Policies', 'cat_val': 'orders'},
    {'title': 'Buntis Congress 2024', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2024'},
    {'title': 'Buntis Congress 2025', 'url': 'projects.project_year', 'category': 'Projects', 'year': '2025'},
    {'title': 'Vision and Mission Statement', 'url': 'main.vision_mission', 'category': 'About'},
    {'title': 'Contact the GAD Office', 'url': 'main.contact', 'category': 'About'},
    {'title': 'Latest News and Updates', 'url': 'main.news_hub', 'category': 'News'},
    {'title': 'GAD Committee Members', 'url': 'main.gad_committee', 'category': 'About'},
    {'title': 'Privacy Policy and Data Protection', 'url': 'legal.privacy_policy', 'category': 'Legal'},
    {'title': 'Terms of Use and Conditions', 'url': 'legal.terms_conditions', 'category': 'Legal'},
    {'title': 'System Developers Team', 'url': 'legal.developers', 'category': 'Team'},
    {'title': 'GAD Events Calendar', 'url': 'calendar.calendar_view', 'category': 'Calendar'},
    {'title': 'GAD Knowledge Products and IEC', 'url': 'main.knowledge_products', 'category': 'Resources'},
    {'title': 'Livelihood Program', 'url': 'main.livelihood_program', 'category': 'Resources'},
]

@main_bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = []
    if query:
        results = [item for item in searchable_content if query.lower() in item['title'].lower()]
    return render_template('search_results.html', query=query, results=results)

@main_bp.route('/api/suggestions')
def get_suggestions():
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 2:
        return jsonify([])
    matches = [item['title'] for item in searchable_content if query in item['title'].lower()]
    return jsonify(matches[:5])