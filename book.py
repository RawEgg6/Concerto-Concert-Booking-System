from flask import Flask, session, render_template, Blueprint, sessions, flash, redirect, url_for, request
from db import get_db_connection

book_bp = Blueprint('book', __name__)

@book_bp.route('/book/<int:concert_id>')
def book_concert(concert_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in first to book a concert!', 'error')
        return redirect(url_for('auth.login'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))
    
    try:
        cursor = db.cursor()
        
        # Get available tickets
        cursor.execute("""
            SELECT t.ticket_id, s.row_no, s.seat_no, s.seat_type, t.price, t.status
            FROM Tickets t
            JOIN Seats s ON t.seat_id = s.seat_id
            WHERE t.concert_id = %s
            ORDER BY s.row_no, s.seat_no
        """, (concert_id,))
        tickets = cursor.fetchall()
        
        # Get concert details
        cursor.execute("""
            SELECT c.title, v.venue_name, v.location, c.date_time 
            FROM Concerts c
            JOIN Venues v ON c.venue_id = v.venue_id
            WHERE c.concert_id = %s
        """, (concert_id,))
        concert = cursor.fetchone()
        
        # Check if concert exists
        if not concert:
            flash('Concert not found!', 'error')
            return redirect(url_for('index'))
        
        # Pass concert details separately to match your template
        return render_template('booking.html', 
                             tickets=tickets,
                             concert_name=concert[0],  # title
                             concert_venue=concert[1] + ', ' + concert[2],  # venue
                             concert_date=concert[3])   # date
        
    except Exception as e:
        print(f"Error details: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))  # Redirect on error instead of rendering
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@book_bp.route('/confirm_booking', methods=['POST', 'GET'])
def confirm_booking():
    user_id = session.get('user_id')
    ticket_id = request.form.get('ticket_id')
    if not user_id:
        flash('You need to log in first to proceed with booking!', 'error')
        return redirect(url_for('auth.login'))
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))    
    try:
        cursor = db.cursor()
        cursor.execute("""SELECT c.title, a.artist_name, v.venue_name, v.location,
                       c.date_time, s.row_no, s.seat_no, t.price
                       FROM Tickets t
                       JOIN Seats s ON t.seat_id = s.seat_id
                       JOIN Concerts c ON t.concert_id = c.concert_id
                       JOIN Artists a ON c.artist_id = a.artist_id
                       JOIN Venues v ON c.venue_id = v.venue_id
                       WHERE t.ticket_id = %s AND t.status != 'sold'""",
                       (ticket_id,))
        ticket_details = cursor.fetchone()
        
        if not ticket_details:
            flash('Ticket not found or unavailable!', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        print(f"Error details: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return render_template('confirm_booking.html',
                            ticket_id=ticket_id,
                            concert_name=ticket_details[0],
                            artist_name=ticket_details[1],
                            venue_name=ticket_details[2],
                            venue_location=ticket_details[3],
                            concert_date=ticket_details[4],
                            row_no=ticket_details[5],
                            seat_no=ticket_details[6],
                            price=ticket_details[7]
                    )

@book_bp.route('/ticket_details')
def ticket_details():
    booking_id = request.args.get('booking_id')
    user_id = session.get('user_id')

    if not user_id:
        flash('You need to log in first to view ticket details!', 'error')
        return redirect(url_for('auth.login'))
    
    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')    
        return redirect(url_for('index'))
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.title, a.artist_name, v.venue_name, v.location,
                   c.date_time, s.row_no, s.seat_no, t.price, b.status
            FROM Bookings b
            JOIN Tickets t ON b.ticket_id = t.ticket_id
            JOIN Seats s ON t.seat_id = s.seat_id
            JOIN Concerts c ON t.concert_id = c.concert_id
            JOIN Artists a ON c.artist_id = a.artist_id
            JOIN Venues v ON c.venue_id = v.venue_id
            WHERE b.booking_id = %s AND b.user_id = %s
        """, (booking_id, user_id))
        ticket_details = cursor.fetchone()
        if not ticket_details:
            flash('Ticket not found or unavailable!', 'error')
            return redirect(url_for('index'))

    except Exception as e:
        print(f"Error details: {e}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return render_template('ticket_details.html',
                            concert_name=ticket_details[0],
                            artist_name=ticket_details[1],
                            venue_name=ticket_details[2],
                            venue_location=ticket_details[3],
                            concert_date=ticket_details[4],
                            row_no=ticket_details[5],
                            seat_no=ticket_details[6],
                            price=ticket_details[7],
                            booking_status=ticket_details[8]
                    )
