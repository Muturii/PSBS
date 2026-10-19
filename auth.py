from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        role = request.form.get('role', 'citizen')

        if User.find_by_email(email):
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        User.create_user(full_name, email, phone, password, role)
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.find_by_email(email)

        if user and User.verify_password(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['full_name']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('citizen.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))