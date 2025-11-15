from flask import Flask, session, render_template, Blueprint, flash, redirect, url_for, request
from db import get_db_connection

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))

    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))
    
    user = None
    bookings = []
    artist_concerts = []
    user_role = 'customer'
    artist_genre = None
    cursor = None
    
    try:
        cursor = db.cursor()
        
        # Get user info
        cursor.execute("""
            SELECT name, email, phone, role FROM Users WHERE user_id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_role = user[3]
        
        # If user is an artist, get their concerts and genre
        if user_role == 'artist':
            # Get artist genre
            cursor.execute("""
                SELECT genre FROM Artists WHERE user_id = %s
            """, (user_id,))
            artist_data = cursor.fetchone()
            if artist_data:
                artist_genre = artist_data[0]
            
            # Get artist's concerts
            cursor.execute("""
                SELECT c.concert_id, c.title, c.date_time, v.venue_name, v.location,
                       COUNT(DISTINCT t.ticket_id) as total_tickets
                FROM Concerts c
                JOIN Artists a ON c.artist_id = a.artist_id
                JOIN Venues v ON c.venue_id = v.venue_id
                LEFT JOIN Tickets t ON c.concert_id = t.concert_id
                WHERE a.user_id = %s
                GROUP BY c.concert_id, c.title, c.date_time, v.venue_name, v.location
                ORDER BY c.date_time DESC
            """, (user_id,))
            concerts = cursor.fetchall()
            
            artist_concerts = [{
                'concert_id': c[0],
                'title': c[1],
                'date_time': c[2],
                'venue_name': c[3],
                'location': c[4],
                'total_tickets': c[5]
            } for c in concerts]
        
        # Get bookings (for all users)
        cursor.execute("""
            SELECT c.title, a.artist_name, v.venue_name, v.location,
                   c.date_time, s.row_no, s.seat_no, t.price, b.status, b.booking_id
            FROM Bookings b
            JOIN Tickets t ON b.ticket_id = t.ticket_id
            JOIN Seats s ON t.seat_id = s.seat_id
            JOIN Concerts c ON t.concert_id = c.concert_id
            JOIN Artists a ON c.artist_id = a.artist_id
            JOIN Venues v ON c.venue_id = v.venue_id
            WHERE b.user_id = %s 
            ORDER BY b.booking_time DESC
        """, (user_id,))
        bookings_data = cursor.fetchall()
        
        bookings = [{
            'concert_name': b[0],
            'artist_name': b[1],
            'venue_name': b[2],
            'venue_location': b[3],
            'concert_date': b[4],
            'row_no': b[5],
            'seat_no': b[6],
            'price': b[7],
            'status': b[8],
            'booking_id': b[9]
        } for b in bookings_data]

    except Exception as e:
        print(f"Error fetching user profile: {e}")
        flash('Could not retrieve profile information.', 'error')

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.login'))

    return render_template('profile.html', 
                          name=user[0], 
                          email=user[1], 
                          phone=user[2],
                          user_role=user_role,
                          artist_genre=artist_genre,
                          artist_concerts=artist_concerts,
                          bookings=bookings)

@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))
    
    # Initialize variables
    user = None
    cursor = None
    
    try:
        cursor = db.cursor()
        if request.method == 'POST':
            name = request.form.get('name')
            phone = request.form.get('phone')
            # Don't update email since it's disabled in the form
            session['name'] = name  # Update session info if needed
            cursor.execute("""
                            UPDATE Users SET name=%s, phone=%s WHERE user_id=%s
                            """, (name, phone, user_id))
            db.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile.profile'))
        else:
            cursor.execute("""
                            SELECT name, email, phone FROM Users WHERE user_id = %s
                            """, (user_id,))
            user = cursor.fetchone()
            
    except Exception as e:
        print(f"Error editing user profile: {e}")
        flash('Could not update profile information.', 'error')
        return redirect(url_for('profile.profile'))
        
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
    
    # Check if user was found
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.login'))
        
    return render_template('edit_profile.html', name=user[0], email=user[1], phone=user[2])