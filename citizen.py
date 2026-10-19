from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import ServiceRequest
from werkzeug.utils import secure_filename
import os
from functools import wraps

citizen_bp = Blueprint('citizen', __name__)

def citizen_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access the citizen portal.', 'warning')
            return redirect(url_for('auth.login', role='citizen'))
        if session.get('role') != 'citizen':
            flash('Admin account detected. Redirected to Admin Command Center.', 'info')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@citizen_bp.route('/dashboard')
@citizen_required
def dashboard():
    requests_list = ServiceRequest.get_by_user(session['user_id'])
    return render_template('citizen_dashboard.html', requests=requests_list)

@citizen_bp.route('/new', methods=['GET', 'POST'])
@citizen_required
def new_request():
    if request.method == 'POST':
        category = request.form.get('category')
        location = request.form.get('location')
        description = request.form.get('description')
        
        image_filename = None
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            
            image_filename = f"{session['user_id']}_{filename}"
            image_file.save(os.path.join(upload_folder, image_filename))
            
        ServiceRequest.create(session['user_id'], category, location, description, image_filename)
        flash('Service request submitted successfully!', 'success')
        return redirect(url_for('citizen.dashboard'))
        
    return render_template('new_request.html')

@citizen_bp.route('/rate/<request_id>', methods=['POST'])
@citizen_required
def rate_request(request_id):
    rating = request.form.get('rating')
    comment = request.form.get('rating_comment', '')
    
    if rating:
        ServiceRequest.add_rating(request_id, rating, comment)
        flash('Thank you! Your feedback has been recorded.', 'success')
        
    return redirect(url_for('citizen.dashboard'))