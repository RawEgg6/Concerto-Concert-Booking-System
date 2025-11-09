# artist.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from datetime import datetime

artist_bp = Blueprint('artist', __name__)

@artist_bp.route('/apply_artist', methods=['GET', 'POST'])
def apply_artist():
    user_id = session.get('user_id')
    
    # Check if user is logged in
    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))

    role = session.get('role')
    if role == 'artist':
        flash('You are already a verified artist!', 'info')
        return redirect(url_for('profile.profile'))

    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('profile.profile'))
    
    cursor = None
    
    try:
        cursor = db.cursor()
        
        # Check if user already has a pending or rejected application
        cursor.execute("""
            SELECT artist_id, status FROM Artists WHERE user_id = %s
        """, (user_id,))
        existing_application = cursor.fetchone()
        
        if existing_application:
            status = existing_application[1]
            if status == 'pending':
                flash('You already have a pending application. Please wait for review.', 'info')
                return redirect(url_for('profile.profile'))
            elif status == 'approved':
                flash('Your application was already approved!', 'success')
                return redirect(url_for('profile.profile'))
            # If rejected, allow them to reapply (continue to form)
        
        if request.method == 'POST':
            # Get form data
            artist_name = request.form.get('artist_name', '').strip()
            genre = request.form.get('genre', '').strip()
            country = request.form.get('country', '').strip()
            bio = request.form.get('bio', '').strip()
            instagram_url = request.form.get('instagram_url', '').strip()
            twitter_url = request.form.get('twitter_url', '').strip()
            spotify_url = request.form.get('spotify_url', '').strip()
            youtube_url = request.form.get('youtube_url', '').strip()
            website_url = request.form.get('website_url', '').strip()
            proof_description = request.form.get('proof_description', '').strip()
            
            # Validate required fields
            if not all([artist_name, genre, country, bio, proof_description]):
                flash('Please fill in all required fields!', 'error')
                return render_template('apply_artist.html')
            
            # Validate minimum length
            if len(bio) < 50:
                flash('Bio must be at least 50 characters long!', 'error')
                return render_template('apply_artist.html')
            
            if len(proof_description) < 100:
                flash('Proof description must be at least 100 characters long!', 'error')
                return render_template('apply_artist.html')
            
            # If user has a rejected application, update it
            if existing_application and existing_application[1] == 'rejected':
                cursor.execute("""
                    UPDATE Artists 
                    SET artist_name = %s, genre = %s, country = %s, bio = %s,
                        instagram_url = %s, twitter_url = %s, spotify_url = %s,
                        youtube_url = %s, website_url = %s, proof_description = %s,
                        status = 'pending', application_date = %s, 
                        rejection_reason = NULL, approved_date = NULL, approved_by = NULL
                    WHERE user_id = %s
                """, (artist_name, genre, country, bio, instagram_url, twitter_url,
                      spotify_url, youtube_url, website_url, proof_description,
                      datetime.now(), user_id))
            else:
                # Create new application
                cursor.execute("""
                    INSERT INTO Artists 
                    (user_id, artist_name, genre, country, bio, instagram_url, 
                     twitter_url, spotify_url, youtube_url, website_url, 
                     proof_description, status, application_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)
                """, (user_id, artist_name, genre, country, bio, instagram_url,
                      twitter_url, spotify_url, youtube_url, website_url,
                      proof_description, datetime.now()))
            
            db.commit()
            
            flash('Application submitted successfully! We will review it shortly.', 'success')
            return redirect(url_for('profile.profile'))
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error in artist application: {e}")
        flash('An error occurred while submitting your application. Please try again.', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    return render_template('apply_artist.html')


@artist_bp.route('/create_concert', methods=['GET', 'POST'])
def create_concert():
    user_id = session.get('user_id')
    
    # Check if user is logged in
    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('profile.profile'))
    
    cursor = None
    venues = []
    
    try:
        cursor = db.cursor()
        
        # Check if user is a verified artist
        cursor.execute("""
            SELECT a.artist_id, u.role, a.status 
            FROM Users u
            LEFT JOIN Artists a ON u.user_id = a.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('User not found!', 'error')
            return redirect(url_for('profile.profile'))
        
        artist_id = user_data[0]
        user_role = user_data[1]
        artist_status = user_data[2] if user_data[2] else None
        
        # Check if user is an artist
        if user_role != 'artist':
            flash('Only verified artists can create concerts!', 'error')
            return redirect(url_for('profile.profile'))
        
        # Check if artist application is approved
        if artist_status != 'approved':
            flash('Your artist application is still pending approval!', 'warning')
            return redirect(url_for('profile.profile'))
        
        # Get all venues for the dropdown
        cursor.execute("""
            SELECT venue_id, venue_name, location, capacity 
            FROM Venues 
            ORDER BY venue_name
        """)
        venues_data = cursor.fetchall()
        
        venues = [{
            'venue_id': v[0],
            'venue_name': v[1],
            'location': v[2],
            'capacity': v[3]
        } for v in venues_data]
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            date_time_str = request.form.get('date_time', '').strip()
            venue_id = request.form.get('venue_id', '').strip()
            gold_price = request.form.get('gold_price', '').strip()
            silver_price = request.form.get('silver_price', '').strip()
            bronze_price = request.form.get('bronze_price', '').strip()
            
            # Validate required fields
            if not all([title, date_time_str, venue_id, gold_price, silver_price, bronze_price]):
                flash('Please fill in all required fields!', 'error')
                return render_template('create_concert.html', 
                                      venues=venues,
                                      min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
            
            # Validate prices are valid numbers
            try:
                gold_price = float(gold_price)
                silver_price = float(silver_price)
                bronze_price = float(bronze_price)
                
                if gold_price <= 0 or silver_price <= 0 or bronze_price <= 0:
                    flash('All ticket prices must be greater than 0!', 'error')
                    return render_template('create_concert.html', 
                                          venues=venues,
                                          min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
                
                # Optional: Validate pricing hierarchy
                if gold_price <= silver_price or silver_price <= bronze_price:
                    flash('Gold price should be greater than Silver, and Silver greater than Bronze!', 'warning')
                    # You can choose to return here or just show warning and continue
                    
            except ValueError:
                flash('Invalid price format!', 'error')
                return render_template('create_concert.html', 
                                      venues=venues,
                                      min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
            
            # Validate date is in the future
            try:
                concert_datetime = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M')
                if concert_datetime <= datetime.now():
                    flash('Concert date must be in the future!', 'error')
                    return render_template('create_concert.html', 
                                          venues=venues,
                                          min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
            except ValueError:
                flash('Invalid date format!', 'error')
                return render_template('create_concert.html', 
                                      venues=venues,
                                      min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
            
            # Check if venue exists
            cursor.execute("SELECT venue_id FROM Venues WHERE venue_id = %s", (venue_id,))
            if not cursor.fetchone():
                flash('Invalid venue selected!', 'error')
                return render_template('create_concert.html', 
                                      venues=venues,
                                      min_datetime=datetime.now().strftime('%Y-%m-%dT%H:%M'))
            
            # Insert concert into database
            cursor.execute("""
                INSERT INTO Concerts (title, artist_id, venue_id, date_time)
                VALUES (%s, %s, %s, %s)
            """, (title, artist_id, venue_id, concert_datetime))
            
            db.commit()
            concert_id = cursor.lastrowid
            
            # Call the stored procedure to generate tickets
            try:
                cursor.callproc('generate_concert_tickets', 
                               [concert_id, gold_price, silver_price, bronze_price])
                db.commit()
                
                # Get count of tickets generated
                cursor.execute("""
                    SELECT COUNT(*) FROM Tickets WHERE concert_id = %s
                """, (concert_id,))
                ticket_count = cursor.fetchone()[0]
                
                flash(f'Concert "{title}" created successfully with {ticket_count} tickets! 🎉', 'success')
                
            except Exception as proc_error:
                db.rollback()
                print(f"Error calling stored procedure: {proc_error}")
                flash('Concert created but failed to generate tickets. Please contact support.', 'warning')
            
            return redirect(url_for('profile.profile'))
        
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error creating concert: {e}")
        flash('An error occurred while creating the concert. Please try again.', 'error')
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    # For GET request
    min_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')
    
    return render_template('create_concert.html', 
                          venues=venues,
                          min_datetime=min_datetime)