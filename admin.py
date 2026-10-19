import re
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from app.models import ServiceRequest
from app import mongo
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the administrator panel.', 'warning')
            return redirect(url_for('auth.login', role='admin'))
        if session.get('role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('citizen.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()
    
    query = {}
    if status_filter:
        query['status'] = status_filter
        
    if search_query:
        regex = re.compile(search_query, re.IGNORECASE)
        query['$or'] = [
            {'category': regex},
            {'location': regex},
            {'description': regex}
        ]
        
    requests_list = list(mongo.db.requests.find(query).sort('_id', -1))
    analytics = ServiceRequest.get_analytics()
    
    return render_template(
        'admin_dashboard.html', 
        requests=requests_list, 
        analytics=analytics, 
        current_status=status_filter,
        current_search=search_query
    )

@admin_bp.route('/update/<request_id>', methods=['POST'])
@admin_required
def update_request(request_id):
    status = request.form.get('status')
    comment = request.form.get('admin_comment', '')
    
    ServiceRequest.update_status(request_id, status, comment)
    
    flash('Request status updated and logged to history.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/export/csv')
@admin_required
def export_csv():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()
    
    query = {}
    if status_filter:
        query['status'] = status_filter
        
    if search_query:
        regex = re.compile(search_query, re.IGNORECASE)
        query['$or'] = [
            {'category': regex},
            {'location': regex},
            {'description': regex}
        ]
        
    requests_list = list(mongo.db.requests.find(query).sort('_id', -1))

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Request ID', 'Category', 'Location', 'Description', 'Status', 'Admin Comment', 'Created At'])
    
    for req in requests_list:
        created_at = req.get('created_at', '').strftime('%Y-%m-%d %H:%M:%S') if hasattr(req.get('created_at'), 'strftime') else str(req.get('created_at', ''))
        writer.writerow([
            str(req.get('_id')),
            req.get('category', ''),
            req.get('location', ''),
            req.get('description', ''),
            req.get('status', ''),
            req.get('admin_comment', ''),
            created_at
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=service_requests_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response