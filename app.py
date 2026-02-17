from flask import Flask, render_template

app = Flask(__name__)

# --- MAIN ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ABOUT SECTION ---
@app.route('/about')
def about():
    return render_template('about/about.html')

@app.route('/about/vision-mission')
def vision_mission():
    return render_template('about/vision-mission.html')

@app.route('/about/org-structure')
def org_structure():
    return render_template('about/org-structure.html')

@app.route('/about/gad-committee')
def gad_committee():
    return render_template('about/gad-committee.html')

@app.route('/about/contact')
def contact():
    return render_template('about/contact.html')

# --- POLICIES & REPORTS ---
@app.route('/policies/<category>')
def policies(category):
    # Mapping the URL parameter to the specific file in the /templates/policies/ folder
    template_map = {
        'circulars': 'policies/circulars.html',
        'resolutions': 'policies/resolution.html',
        'memoranda': 'policies/memoranda.html',
        'orders': 'policies/office-orders.html',
        'hub': 'policies/policies.html'
    }
    # Default to the general policies hub if category not found
    target_template = template_map.get(category, 'policies/policies.html')
    return render_template(target_template)

@app.route('/reports')
def reports():
    return render_template('policies/reports.html')

# --- PROJECTS ---
@app.route('/projects')
def projects_hub():
    return render_template('projects/projects.html')

@app.route('/projects/year/<year>')
def project_year(year):
    return render_template('projects/project-year.html', year=year)

@app.route('/projects/archive')
def projects_archive():
    return render_template('projects/archive.html')

# --- NEWS ---
@app.route('/news')
def news_hub():
    return render_template('news/news.html')

@app.route('/news/article-1')
def news_detail():
    return render_template('news/news-detail.html')

# --- LEGAL SECTION (NEW) ---
@app.route('/legal/privacy-policy')
def privacy_policy():
    return render_template('legal/privacy-policy.html')

@app.route('/legal/terms-conditions')
def terms_conditions():
    return render_template('legal/terms-conditions.html')

# --- DEVELOPER TEAM (NEW) ---
@app.route('/team/developers')
def developers():
    return render_template('team/developers.html')

# --- ERROR HANDLERS (Optional but recommended) ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404 # Or a custom 404.html

if __name__ == '__main__':
    app.run(debug=True)