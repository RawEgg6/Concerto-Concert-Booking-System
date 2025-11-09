from flask import Flask, render_template, flash, session, redirect, url_for
import os
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv(override=True)

class Config:
    # Flask requires this key for sessions and flashing messages
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'a-temporary-fallback-secret'
    
    # You use these variables in your db.py
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')


app = Flask(__name__)
app.config.from_object(Config)

app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

@app.context_processor
def inject_user():
    """Make user session data available to all templates"""
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role')
    }


@app.route('/')
def home():
    role = session.get('role')
    user_id = session.get('user_id')
    return render_template('base.html', user_id=user_id, role=role)

@app.route('/index')
def index():
    user_id = session.get('user_id')
    username = session.get('name')
    if not username:
        username = "Guest"

    concerts = []
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
    try:
        cursor = db.cursor()
        cursor.execute("""
                       SELECT c.concert_id, c.title, c.date_time, a.artist_name, 
                       a.genre, v.venue_name, v.location FROM 
                       Concerts c, Artists a, Venues v 
                       WHERE c.artist_id = a.artist_id 
                       AND c.venue_id = v.venue_id LIMIT 5
                       """)
        concerts = cursor.fetchall()
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        concerts = []
    finally:
        cursor.close()
        db.close()
    print(concerts)
    return render_template('index.html', username=username, concerts=concerts)

from auth import auth_bp
app.register_blueprint(auth_bp)

from book import book_bp
app.register_blueprint(book_bp)

from payment import payment_bp
app.register_blueprint(payment_bp)

from profile import profile_bp
app.register_blueprint(profile_bp)

from artist import artist_bp
app.register_blueprint(artist_bp)

from admin import admin_bp
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)
