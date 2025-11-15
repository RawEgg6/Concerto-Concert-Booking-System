1. -- Query to retrieve the first 5 concerts with their details
SELECT c.concert_id, c.title, c.date_time, a.artist_name, 
                       a.genre, v.venue_name, v.location FROM 
                       Concerts c, Artists a, Venues v 
                       WHERE c.artist_id = a.artist_id 
                       AND c.venue_id = v.venue_id LIMIT 5

2. -- Query to authenticate a user by email
SELECT password, user_id, name, role FROM Users WHERE email = %s

3. -- Query to get user details by email
SELECT * FROM Users WHERE email = %s

4. -- Query to add a new user
INSERT INTO Users (email, password) VALUES (%s, %s)

5. -- Query to retrieve tickets for a specific concert
SELECT t.ticket_id, s.row_no, s.seat_no, s.seat_type, t.price, t.status
            FROM Tickets t
            JOIN Seats s ON t.seat_id = s.seat_id
            WHERE t.concert_id = %s
            ORDER BY s.row_no, s.seat_no

6. -- Query to get concert details by concert ID
SELECT c.title, v.venue_name, v.location, c.date_time 
            FROM Concerts c
            JOIN Venues v ON c.venue_id = v.venue_id
            WHERE c.concert_id = %s

5. -- Query to get ticket details by ticket ID
SELECT c.title, a.artist_name, v.venue_name, v.location,
                       c.date_time, s.row_no, s.seat_no, t.price
                       FROM Tickets t
                       JOIN Seats s ON t.seat_id = s.seat_id
                       JOIN Concerts c ON t.concert_id = c.concert_id
                       JOIN Artists a ON c.artist_id = a.artist_id
                       JOIN Venues v ON c.venue_id = v.venue_id
                       WHERE t.ticket_id = %s AND t.status != 'sold'            

6. -- Query to retrieve booking details by booking ID and user ID
SELECT c.title, a.artist_name, v.venue_name, v.location,
                   c.date_time, s.row_no, s.seat_no, t.price, b.status
            FROM Bookings b
            JOIN Tickets t ON b.ticket_id = t.ticket_id
            JOIN Seats s ON t.seat_id = s.seat_id
            JOIN Concerts c ON t.concert_id = c.concert_id
            JOIN Artists a ON c.artist_id = a.artist_id
            JOIN Venues v ON c.venue_id = v.venue_id
            WHERE b.booking_id = %s AND b.user_id = %s

7. -- Query to retrieve all tickets held by a user
hold_ticket    

8. -- Query to create a new booking
create_booking

9. -- Query to complete a booking
SET @p_user_id = %s, @p_ticket_id = %s;
CALL complete_booking(@p_user_id, @p_ticket_id, @p_booking_id);
SELECT @p_booking_id

10. -- Query to cancel a booking
SET @u=%s, @t=%s;
CALL cancel_booking(@u, @t, @b);
SELECT @b;

11. -- Query to get user details by user ID
SELECT name, email, phone, role FROM Users WHERE user_id = %s

12. -- Query to get artist genre by user ID
SELECT genre FROM Artists WHERE user_id = %s

13. -- Query to get concerts by artist user ID
SELECT c.concert_id, c.title, c.date_time, v.venue_name, v.location,
                       COUNT(DISTINCT t.ticket_id) as total_tickets
                FROM Concerts c
                JOIN Artists a ON c.artist_id = a.artist_id
                JOIN Venues v ON c.venue_id = v.venue_id
                LEFT JOIN Tickets t ON c.concert_id = t.concert_id
                WHERE a.user_id = %s
                GROUP BY c.concert_id, c.title, c.date_time, v.venue_name, v.location
                ORDER BY c.date_time DESC

14. -- Query to retrieve all bookings by user ID
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

15. -- Query to update user details
UPDATE Users SET name=%s, phone=%s WHERE user_id=%s

16. -- Query to get artist ID and status by user ID
SELECT artist_id, status FROM Artists WHERE user_id = %s

17. -- Query to update artist application details
UPDATE Artists 
    SET artist_name = %s, genre = %s, country = %s, bio = %s,
        instagram_url = %s, twitter_url = %s, spotify_url = %s,
        youtube_url = %s, website_url = %s, proof_description = %s,
        status = 'pending', application_date = %s, 
        rejection_reason = NULL, approved_date = NULL, approved_by = NULL
    WHERE user_id = %s

18. -- Query to insert a new artist application
INSERT INTO Artists 
                    (user_id, artist_name, genre, country, bio, instagram_url, 
                     twitter_url, spotify_url, youtube_url, website_url, 
                     proof_description, status, application_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s)

19. -- Query to get artist ID, role, and status by user ID
SELECT a.artist_id, u.role, a.status 
            FROM Users u
            LEFT JOIN Artists a ON u.user_id = a.user_id
            WHERE u.user_id = %s

20. -- Query to get all venues
SELECT venue_id, venue_name, location, capacity 
            FROM Venues 
            ORDER BY venue_name

21. -- Query to get a venue by venue ID
SELECT venue_id FROM Venues WHERE venue_id = %s

22. -- Query to add a new concert
INSERT INTO Concerts (title, artist_id, venue_id, date_time)
                VALUES (%s, %s, %s, %s)

23. -- Query to generate concert tickets
CALL generate_concert_tickets(%s)

24. -- Query to count tickets for a concert
SELECT COUNT(*) FROM Tickets WHERE concert_id = %s

25. -- Query to get user role by user ID
SELECT role FROM Users WHERE user_id = %s

26. --Administrative queries for artist applications
-- Pending applications
SELECT COUNT(*) FROM Artists WHERE status = 'pending';

-- Approved artists
SELECT COUNT(*) FROM Artists WHERE status = 'approved';

-- Rejected applications
SELECT COUNT(*) FROM Artists WHERE status = 'rejected';

-- Total applications
SELECT COUNT(*) FROM Artists;

27. -- Query to get pending artist applications with user email
SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'pending'
            ORDER BY a.application_date DESC
 
28. -- Query to get approved artists with user email
SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email, a.approved_date
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'approved'
            ORDER BY a.approved_date DESC

29. -- Query to get rejected artist applications with user email
SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.status = 'rejected'
            ORDER BY a.application_date DESC

30. -- Query to get all artist applications with user email
SELECT a.artist_id, a.artist_name, a.genre, a.country, a.application_date, a.status,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            ORDER BY a.application_date DESC

31. -- Query to get detailed artist application by artist ID
SELECT a.artist_id, a.artist_name, a.genre, a.country, a.bio,
                   a.instagram_url, a.twitter_url, a.spotify_url, a.youtube_url, a.website_url,
                   a.proof_description, a.status, a.application_date, a.approved_date, a.rejection_reason,
                   u.email
            FROM Artists a
            JOIN Users u ON a.user_id = u.user_id
            WHERE a.artist_id = %s

32. -- Query to get artist name by artist ID
SELECT user_id, artist_name FROM Artists WHERE artist_id = %s

33. -- Query to approve an artist application
UPDATE Artists 
            SET status = 'approved', approved_date = %s, approved_by = %s
            WHERE artist_id = %s

34. -- Query to update user role to artist
UPDATE Users 
            SET role = 'artist'
            WHERE user_id = %s

35. -- Query to reject an artist application
UPDATE Artists 
            SET status = 'rejected', rejection_reason = %s
            WHERE artist_id = %s
