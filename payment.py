from flask import Blueprint, render_template, session, flash, redirect, url_for, request
from db import get_db_connection

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    user_id = session.get('user_id')
    ticket_id = request.form.get('ticket_id')

    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))

    db = get_db_connection()
    if not db:
        flash('Database connection failed!', 'error')
        return redirect(url_for('index'))
    try:
        cursor = db.cursor()
        # Call stored procedure to hold the ticket
        cursor.callproc('hold_ticket', (user_id, ticket_id))
        db.commit()

        flash('Ticket temporarily held. Proceed to payment.', 'info')
        
        # Redirect user to payment page
        return redirect(url_for('payment.simulate_payment', ticket_id=ticket_id))

    except Exception as e:
        db.rollback()
        print(f"Error during hold_ticket: {e}")
        flash('Could not hold ticket. It may already be reserved.', 'error')
        return redirect(url_for('index'))

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@payment_bp.route('/payment_gateway', methods=['POST',])
def payment_gateway():
    
    user_id = session.get('user_id')
    ticket_id = request.form.get('ticket_id')
    payment_method = request.form.get('payment_method')
    payment_status = request.form.get('payment_status')  # e.g., 'success' or 'failed'
    amount = request.form.get('amount')


    if not user_id:
        flash('You need to log in first!', 'error')
        return redirect(url_for('auth.login'))

    db = get_db_connection()
    if not db:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))

    try:
        cursor = db.cursor()

        cursor.callproc('create_booking', (user_id, ticket_id, amount, payment_method))

        db.commit()


        if payment_status == 'success':

            # Call confirm_booking stored procedure
            cursor.execute("SET @p_user_id = %s, @p_ticket_id = %s;", (user_id, ticket_id))
            cursor.execute("CALL complete_booking(@p_user_id, @p_ticket_id, @p_booking_id);")
            cursor.execute("SELECT @p_booking_id;")
            booking_id = cursor.fetchone()[0]

            db.commit()

            flash('Payment successful! Your booking is confirmed.', 'success')
        else:

            # Payment failed — rollback the reservation
            cursor.execute("SET @u=%s, @t=%s;", (user_id, ticket_id))
            cursor.execute("CALL cancel_booking(@u, @t, @b);")
            cursor.execute("SELECT @b;")
            booking_id = cursor.fetchone()[0]

            db.commit()
            
            flash('Payment failed. Ticket released.', 'error')

        return redirect(url_for('book.ticket_details', booking_id=booking_id))

    except Exception as e:
        db.rollback()
        print(f"Error during payment_gateway: {e}")
        flash('An error occurred while confirming payment.', 'error')
        return redirect(url_for('index'))

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@payment_bp.route('/simulate_payment', methods=['GET', 'POST'])
def simulate_payment():
    ticket_id = request.args.get('ticket_id')  # passed in URL
    user_id = session.get('user_id')

    if not user_id:
        flash('You need to log in to simulate payment.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        payment_status = request.form.get('payment_status')
        amount = request.form.get('amount')

        # Redirect to your existing /payment_gateway route
        return redirect(url_for('payment.payment_gateway',
                                ticket_id=ticket_id,
                                payment_method=payment_method,
                                status=payment_status,
                                amount=amount))

    return render_template('simulate_payment.html', ticket_id=ticket_id)
