from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Hashes a password for secure storage."""
    return generate_password_hash(password)

def check_password(hashed_password, user_password):
    """Checks a hashed password against a user-provided password."""
    return check_password_hash(hashed_password, user_password)

auth_bp = Blueprint('auth', __name__)   

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add logic to verify user credentials
        username = request.form['username']
        password = request.form['password']
        db = get_db_connection()
        if not db:
            flash('Database connection error!', 'error')
            return render_template('login.html')
        try:
            cursor = db.cursor()
            cursor.execute("SELECT password, user_id, name, role FROM Users WHERE email = %s", (username,))
            user = cursor.fetchone()
            if user and check_password(user[0], password):
                session['user_id'] = user[1]
                session['name'] = user[2]
                session['role'] = user[3]
                flash('Login successful!', 'success')
                if user[3] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('index'))
            else:
                flash('Invalid credentials!', 'error')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return render_template('base.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Validate input
        if len(email) < 2:
            flash('Email must be at least 2 characters long!', 'error')
            return render_template('signup.html')
        
        if len(password) < 2:
            flash('Password must be at least 2 characters long!', 'error')
            return render_template('signup.html')

        hashed_password = hash_password(password)

        # Database operations
        db = get_db_connection()
        if not db:
            flash('Database connection error!', 'error')
            return render_template('signup.html')

        try:
            cursor = db.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT * FROM Users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                flash('Email already exists!', 'error')
            else:
                # Insert new user with email and password
                cursor.execute(
                    "INSERT INTO Users (email, password) VALUES (%s, %s)", 
                    (email, hashed_password)
                )
                db.commit()
                flash('Account created successfully!', 'success')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            db.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            cursor.close()
            db.close()

    return render_template('signup.html')

