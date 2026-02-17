from flask import Blueprint, render_template, request

main_bp = Blueprint('main', __name__)

RESOURCES = [
    {'title': 'Gender Equality Act', 'description': 'A comprehensive guide to policies in Rodriguez.', 'url': '/policies/circulars'},
    {'title': 'Annual GAD Report 2024', 'description': 'Summary of all GAD achievements for the year 2024.', 'url': '/policies/reports'},
    {'title': 'Women Empowerment Workshop', 'description': 'Upcoming project for livelihood training.', 'url': '/projects/2025'},
    {'title': 'Livelihood Programs', 'description': 'Financial support for local entrepreneurs.', 'url': '/projects/2024'},
]

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/search')
def search():
    query = request.args.get('q', '').lower()
    
    results = []
    if query:
        results = [
            item for item in RESOURCES 
            if query in item['title'].lower() or query in item['description'].lower()
        ]
    
    return render_template('search_results.html', results=results, query=query)

@main_bp.route('/about')
def about():
    return render_template('about/about.html')

@main_bp.route('/about/vision-mission')
def vision_mission():
    return render_template('about/vision-mission.html')

@main_bp.route('/about/org-structure')
def org_structure():
    return render_template('about/org-structure.html')

@main_bp.route('/about/gad-committee')
def gad_committee():
    return render_template('about/gad-committee.html')

@main_bp.route('/about/contact')
def contact():
    return render_template('about/contact.html')

@main_bp.route('/news')
def news_hub():
    return render_template('news/news.html')

@main_bp.route('/news/article-1')
def news_detail():
    return render_template('news/news-detail.html')