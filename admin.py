# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    """Check if current user is admin"""
    user_id = session.get('user_id')
    if not user_id:
        return False
    
    db = get_db_connection()
    if not db:
        return False
    
    try:
        cursor = db.cursor()
        cursor.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result and result[0] == 'admin'
    except:
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if db:
            db.close()

@admin_bp.route('/dashboard')
def dashboard():
    # Check if user is admin
    if not is_admin():
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('profile.profile'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('profile.profile'))
    
    cursor = None
    
    try:
        cursor = db.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM Artists WHERE status = 'pending'")
        pending_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Artists WHERE status = 'approved'")
        approved_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Artists WHERE status = 'rejected'")
        rejected_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Artists")
        total_count = cursor.fetchone()[0]
        
        stats = {
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'total': total_count
        }
        
        # Get pending applications
        cursor.execute("""
            SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'pending'
            ORDER BY a.application_date DESC
        """)
        pending_apps = cursor.fetchall()
        
        pending_applications = [{
            'artist_id': app[0],
            'artist_name': app[1],
            'genre': app[2],
            'country': app[3],
            'application_date': app[4],
            'status': app[5],
            'email': app[6]
        } for app in pending_apps]
        
        # Get approved applications
        cursor.execute("""
            SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email, a.approved_date
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'approved'
            ORDER BY a.approved_date DESC
        """)
        approved_apps = cursor.fetchall()
        
        approved_applications = [{
            'artist_id': app[0],
            'artist_name': app[1],
            'genre': app[2],
            'country': app[3],
            'application_date': app[4],
            'status': app[5],
            'email': app[6],
            'approved_date': app[7]
        } for app in approved_apps]
        
        # Get rejected applications
        cursor.execute("""
            SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'rejected'
            ORDER BY a.application_date DESC
        """)
        rejected_apps = cursor.fetchall()
        
        rejected_applications = [{
            'artist_id': app[0],
            'artist_name': app[1],
            'genre': app[2],
            'country': app[3],
            'application_date': app[4],
            'status': app[5],
            'email': app[6]
        } for app in rejected_apps]
        
        # Get all applications
        cursor.execute("""
            SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            ORDER BY a.application_date DESC
        """)
        all_apps = cursor.fetchall()
        
        all_applications = [{
            'artist_id': app[0],
            'artist_name': app[1],
            'genre': app[2],
            'country': app[3],
            'application_date': app[4],
            'status': app[5],
            'email': app[6]
        } for app in all_apps]
        
    except Exception as e:
        print(f"Error fetching admin dashboard data: {e}")
        flash('An error occurred while loading the dashboard.', 'error')
        stats = {'pending': 0, 'approved': 0, 'rejected': 0, 'total': 0}
        pending_applications = []
        approved_applications = []
        rejected_applications = []
        all_applications = []
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return render_template('admin_dashboard.html',
                          stats=stats,
                          pending_applications=pending_applications,
                          approved_applications=approved_applications,
                          rejected_applications=rejected_applications,
                          all_applications=all_applications)

# Add these routes to admin.py

@admin_bp.route('/review_artist/<int:artist_id>')
def review_artist(artist_id):
    # Check if user is admin
    if not is_admin():
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('profile.profile'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    cursor = None
    artist = None
    
    try:
        cursor = db.cursor()
        
        # Get artist details
        cursor.execute("""
            SELECT a.artist_id, a.artist_name, a.genre, a.country, a.bio,
                   a.instagram_url, a.twitter_url, a.spotify_url, a.youtube_url, a.website_url,
                   a.proof_description, a.status, a.application_date, a.approved_date, a.rejection_reason,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.artist_id = %s
        """, (artist_id,))
        
        artist_data = cursor.fetchone()
        
        if not artist_data:
            flash('Artist not found!', 'error')
            return redirect(url_for('admin.dashboard'))
        
        artist = {
            'artist_id': artist_data[0],
            'artist_name': artist_data[1],
            'genre': artist_data[2],
            'country': artist_data[3],
            'bio': artist_data[4],
            'instagram_url': artist_data[5],
            'twitter_url': artist_data[6],
            'spotify_url': artist_data[7],
            'youtube_url': artist_data[8],
            'website_url': artist_data[9],
            'proof_description': artist_data[10],
            'status': artist_data[11],
            'application_date': artist_data[12],
            'approved_date': artist_data[13],
            'rejection_reason': artist_data[14],
            'email': artist_data[15]
        }
        
    except Exception as e:
        print(f"Error fetching artist details: {e}")
        flash('An error occurred while loading artist details.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return render_template('review_artist.html', artist=artist)


@admin_bp.route('/approve_artist/<int:artist_id>', methods=['POST'])
def approve_artist(artist_id):
    # Check if user is admin
    if not is_admin():
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('profile.profile'))
    
    admin_user_id = session.get('user_id')
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    cursor = None
    
    try:
        cursor = db.cursor()
        
        # Get artist user_id and name
        cursor.execute("""
            SELECT user_id, artist_name FROM Artists WHERE artist_id = %s
        """, (artist_id,))
        artist_data = cursor.fetchone()
        
        if not artist_data:
            flash('Artist not found!', 'error')
            return redirect(url_for('admin.dashboard'))
        
        user_id = artist_data[0]
        artist_name = artist_data[1]
        
        # Update artist status
        cursor.execute("""
            UPDATE Artists 
            SET status = 'approved', approved_date = %s, approved_by = %s
            WHERE artist_id = %s
        """, (datetime.now(), admin_user_id, artist_id))
        
        # Update user role to artist
        cursor.execute("""
            UPDATE Users 
            SET role = 'artist'
            WHERE user_id = %s
        """, (user_id,))
        
        db.commit()
        
        flash(f'Artist "{artist_name}" has been approved successfully! 🎉', 'success')
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error approving artist: {e}")
        flash('An error occurred while approving the artist.', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/reject_artist/<int:artist_id>', methods=['POST'])
def reject_artist(artist_id):
    # Check if user is admin
    if not is_admin():
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('profile.profile'))
    
    rejection_reason = request.form.get('rejection_reason', '').strip()
    
    if not rejection_reason or len(rejection_reason) < 20:
        flash('Please provide a detailed rejection reason (at least 20 characters).', 'error')
        return redirect(url_for('admin.review_artist', artist_id=artist_id))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    cursor = None
    
    try:
        cursor = db.cursor()
        
        # Get artist name
        cursor.execute("""
            SELECT artist_name FROM Artists WHERE artist_id = %s
        """, (artist_id,))
        artist_data = cursor.fetchone()
        
        if not artist_data:
            flash('Artist not found!', 'error')
            return redirect(url_for('admin.dashboard'))
        
        artist_name = artist_data[0]
        
        # Update artist status
        cursor.execute("""
            UPDATE Artists 
            SET status = 'rejected', rejection_reason = %s
            WHERE artist_id = %s
        """, (rejection_reason, artist_id))
        
        db.commit()
        
        flash(f'Application for "{artist_name}" has been rejected.', 'info')
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error rejecting artist: {e}")
        flash('An error occurred while rejecting the artist.', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return redirect(url_for('admin.dashboard'))