# 🎵 Concerto - Concert Booking System

A comprehensive web-based concert booking platform built with Flask that enables users to browse concerts, book tickets, and manage their profiles. The system supports multiple user roles including regular users, artists, and administrators.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [User Roles](#user-roles)
- [Database](#database)
- [Contributing](#contributing)

## ✨ Features

### For Users
- 🎫 Browse and search for upcoming concerts
- 📅 Book concert tickets with seat selection
- 💳 Simulated payment processing
- 👤 User profile management
- 📜 View booking history
- 🎨 Apply to become an artist

### For Artists
- 🎤 Create and manage concerts
- 🎪 Venue management
- 📊 View concert performance data
- 🎭 Manage artist profile with social media links

### For Administrators
- ✅ Review and approve/reject artist applications
- 📈 Dashboard with application statistics
- 👥 User management
- 🔍 Detailed application review system

## 🛠️ Tech Stack

- **Backend**: Flask (Python 3.x)
- **Database**: MySQL
- **Frontend**: HTML, Jinja2 Templates
- **Security**: Werkzeug (Password hashing)
- **Environment Management**: python-dotenv

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- MySQL Server
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/RawEgg6/Concerto-Concert-Booking-System.git
   cd Concerto-Concert-Booking-System
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Create a MySQL database for the application
   - Configure database credentials (see Configuration section)

5. **Create a `.env` file** in the root directory with the following variables:
   ```env
   FLASK_SECRET_KEY=your-secret-key-here
   DB_HOST=localhost
   DB_USER=your-database-username
   DB_PASSWORD=your-database-password
   DB_NAME=your-database-name
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## ⚙️ Configuration

The application uses environment variables for configuration. Create a `.env` file with the following parameters:

| Variable | Description | Example |
|----------|-------------|---------|
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | `your-super-secret-key` |
| `DB_HOST` | MySQL database host | `localhost` |
| `DB_USER` | MySQL database username | `root` |
| `DB_PASSWORD` | MySQL database password | `password123` |
| `DB_NAME` | MySQL database name | `concerto_db` |

## 🚀 Usage

### Creating an Account

1. Navigate to the signup page
2. Enter your email and password
3. Complete registration

### Booking a Concert

1. Log in to your account
2. Browse available concerts on the index page
3. Select a concert and choose your seats
4. Proceed to payment simulation
5. Confirm your booking

### Applying as an Artist

1. Log in as a regular user
2. Navigate to the artist application page
3. Fill in your artist details including:
   - Artist name and genre
   - Biography
   - Social media links (Instagram, Twitter, Spotify, YouTube)
   - Proof of authenticity
4. Submit application for admin review

### Admin Dashboard

1. Log in with admin credentials
2. Access the admin dashboard
3. Review pending artist applications
4. Approve or reject applications with detailed feedback

## 📁 Project Structure

```
Concerto-Concert-Booking-System/
│
├── app.py                  # Main application entry point
├── admin.py               # Admin blueprint and routes
├── artist.py              # Artist-related routes and functionality
├── auth.py                # Authentication (login, signup, logout)
├── book.py                # Booking system routes
├── payment.py             # Payment simulation routes
├── profile.py             # User profile management
├── db.py                  # Database connection handler
├── test.py                # Testing utilities
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── booking.html
│   ├── confirm_booking.html
│   ├── simulate_payment.html
│   ├── profile.html
│   ├── edit_profile.html
│   ├── apply_artist.html
│   ├── create_concert.html
│   ├── admin_dashboard.html
│   ├── review_artist.html
│   └── ticket_details.html
│
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── .env                  # Environment variables (not in repo)
```

## 👥 User Roles

### Regular User (Default)
- Browse concerts
- Book tickets
- Manage profile
- Apply to become an artist

### Artist
- All user permissions
- Create concerts
- Manage venues
- View concert analytics

### Administrator
- Review artist applications
- Approve/reject applications
- Access admin dashboard
- View system statistics

## 🗄️ Database

The application uses MySQL with the following main tables:

- **Users**: User authentication and profile information
- **Artists**: Artist profiles and application status
- **Concerts**: Concert details and scheduling
- **Venues**: Concert venue information
- **Bookings**: Ticket booking records
- **Payments**: Payment transaction records

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection via Flask sessions
- Secure database connections

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is available for educational and personal use.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Developed with ❤️ using Flask**
