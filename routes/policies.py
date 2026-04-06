from flask import Blueprint, render_template
from database import supabase

policies_bp = Blueprint('policies', __name__)

def get_category_template(category):
    return {
        'republic_acts': 'policies/republic-acts.html',
        'resolutions': 'policies/resolution.html',
        'memoranda': 'policies/memoranda.html',
        'orders': 'policies/office-orders.html',
        'hub': 'policies/policies.html'
    }.get(category, 'policies/policies.html')

@policies_bp.route('/policies/<category>')
def policies_hub(category):
    try:
        response = supabase.table('policies').select('*').eq('category', category).order('year', desc=True).execute()
        category_list = response.data
    except Exception:
        category_list = []

    stats = {
        'total': len(category_list),
        'updated': max((p.get('date', '') for p in category_list), default='')
    }

    return render_template(
        get_category_template(category),
        policies=category_list,
        stats=stats,
    )

@policies_bp.route('/reports')
def reports():
    try:
        response = supabase.table('policies').select('*').eq('category', 'reports').order('year', desc=True).execute()
        report_list = response.data
    except Exception:
        report_list = []
    return render_template('policies/reports.html', reports=report_list)

@policies_bp.route("/policies")
def policies_index():
    return render_template("policies/policies.html")

@policies_bp.route("/policies/coming-soon")
def policies_placeholder():
    return render_template("policies/placeholder.html")

@policies_bp.route('/lbp-forms')
def lbp_forms():
    try:
        response = supabase.table('policies').select('*').eq('category', 'lbp_forms').order('year', desc=True).execute()
        form_list = response.data
    except Exception:
        form_list = []
    return render_template('policies/lbp-forms.html', forms=form_list)

@policies_bp.route('/estado-ni-juana')
def estado_ni_juana():
    try:
        response = supabase.table('policies').select('*').eq('category', 'estado_ni_juana').order('year', desc=True).execute()
        report_list = response.data
    except Exception:
        report_list = []
    return render_template('policies/estado-ni-juana.html', reports=report_list)
