# Changelog

## v0.3.1 - PostgreSQL Database Implementation (2025-04-27)

### Added
- PostgreSQL database integration
  - Added PostgreSQL service in docker-compose.yml
  - Configured persistent volume for database data
  - Added psycopg2-binary adapter for PostgreSQL
- Database connection improvements
  - Added connection pool settings
  - Implemented retry logic for database initialization
  - Added connection validation with pool_pre_ping

### Changed
- Updated database connection string to use PostgreSQL
- Enhanced database initialization with error handling
- Improved container startup sequence with depends_on

## v0.3.0 - User Registration Implementation (2025-04-27)

### Added
- User registration functionality
  - Registration form with validation
  - User login system
  - User profile page
  - User ranking system
- New templates
  - register.html for user registration
  - user_login.html for user authentication
  - profile.html for user profile display
- New User model methods
  - create_user for regular user creation
  - find_by_email for email validation
  - get_user_ranking for leaderboard position

### Changed
- Updated navigation to include user login/register links
- Changed default login_view to user login instead of admin login
- Updated index page "Get Started" button to link to registration
- Enhanced User model with additional helper methods

## v0.2.2 - Additional Dependency Fix (2025-04-25)

### Fixed
- Resolved SQLAlchemy compatibility issue
- Added explicit SQLAlchemy version 1.4.46 to requirements

## v0.2.1 - Dependency Fix (2025-04-25)

### Fixed
- Resolved dependency conflict between Flask-Login and Werkzeug
- Pinned package versions to ensure compatibility:
  - Downgraded Flask to 2.0.1
  - Specified Werkzeug 2.0.3
  - Downgraded Flask-Login to 0.5.0
  - Adjusted Flask-SQLAlchemy to 2.5.1

## v0.2.0 - Admin User Implementation (2025-04-25)

### Added
- Admin user functionality
  - Automatic admin user creation on first start
  - Admin login system with Flask-Login
  - Admin dashboard template
  - User authentication and session management
- New dependencies
  - Flask-Bcrypt for password hashing
  - Flask-Login for user session management
- New templates
  - login.html for admin authentication
  - admin_dashboard.html for admin interface
- Environment variables for admin user configuration
- Persistent volume for SQLite database in Docker

### Changed
- Enabled database functionality (previously commented out)
- Updated User model to include admin role and authentication methods
- Enhanced docker-compose.yml with environment variables for admin configuration
- Added admin link to main navigation

## v0.1.0 - Initial Setup (2025-04-24)

### Added
- Basic Flask application structure
  - Main application file (app.py)
  - HTML template for homepage (templates/index.html)
  - CSS styling (static/style.css)
- Database preparation
  - Basic User model (models/user.py)
  - SQLAlchemy configuration (commented out for future use)
- Docker configuration
  - Dockerfile for containerization
  - docker-compose.yml for orchestration
  - .dockerignore file
- Project configuration
  - requirements.txt with dependencies
  - .gitignore file
  - Updated README.md with project structure and instructions

### Features
- "Hello World" landing page with IndyFit branding
- Responsive design with CSS
- Navigation structure for future pages
- Docker and Docker Compose setup for easy deployment
- Prepared database models structure for future implementation