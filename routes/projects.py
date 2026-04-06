import os
from flask import Blueprint, render_template, abort
from database import supabase

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects')
def projects_hub():
    return render_template('projects/projects.html')

@projects_bp.route('/projects/year/<year>')
def project_year(year):
    try:
        response = supabase.table('projects').select('*').eq('year', int(year)).execute()
        projects = response.data
    except Exception as e:
        print(f"Database error: {e}")
        projects = []
    return render_template('projects/project-year.html', year=year, projects=projects)

@projects_bp.route('/projects/archive')
def projects_archive():
    try:
        response = supabase.table('projects').select('year').execute()
        years = sorted(set(p.get('year') for p in response.data), reverse=True)
    except Exception:
        years = []
    return render_template('projects/archive.html', years=years)

@projects_bp.route('/projects/detail/<project_id>')
def project_detail(project_id):
    try:
        response = supabase.table('projects').select('*').eq('id', project_id).execute()
        if not response.data:
            abort(404)
        project = response.data[0]
    except Exception:
        abort(404)
    return render_template('projects/project-detail.html', project=project)