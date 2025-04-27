from flask import Flask, render_template, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from models.user import db, bcrypt, User
from functools import wraps

app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///indyfit.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using them
    'pool_recycle': 300,    # Recycle connections every 5 minutes
}

# Admin user configuration from environment variables
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@indyfit.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')
ADMIN_FIRST_NAME = os.environ.get('ADMIN_FIRST_NAME', 'Admin')
ADMIN_LAST_NAME = os.environ.get('ADMIN_LAST_NAME', 'User')

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Changed default login view to user login
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'danger'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

def admin_required(f):
    """Decorator to require admin access for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def create_admin_if_not_exists():
    """Create an admin user if no admin exists"""
    with app.app_context():
        if User.get_admin_count() == 0:
            print("No admin user found. Creating default admin user...")
            try:
                User.create_admin_user(
                    username=ADMIN_USERNAME,
                    email=ADMIN_EMAIL,
                    password=ADMIN_PASSWORD,
                    first_name=ADMIN_FIRST_NAME,
                    last_name=ADMIN_LAST_NAME
                )
                print(f"Admin user '{ADMIN_USERNAME}' created successfully!")
            except Exception as e:
                print(f"Error creating admin user: {str(e)}")

# Public routes
@app.route('/')
def home():
    return render_template('index.html', title='IndyFit - Fitness for Indianapolis Parks')

@app.route('/about')
def about():
    return render_template('index.html', title='About IndyFit')

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validate form data
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', title='Register')
        
        # Check if username or email already exists
        if User.find_by_username(username):
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html', title='Register')
        
        if User.find_by_email(email):
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html', title='Register')
        
        # Create new user
        try:
            user = User.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'danger')
    
    return render_template('register.html', title='Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.find_by_username(username)
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    
    return render_template('user_login.html', title='Login')

@app.route('/profile')
@login_required
def profile():
    """User profile route"""
    # Mock data for activities
    activities_count = 0
    ranking = User.get_user_ranking(current_user.id)
    recent_activities = []  # This would be populated from a database in a real implementation
    
    return render_template('profile.html',
                          title='My Profile',
                          current_user=current_user,
                          activities_count=activities_count,
                          ranking=ranking,
                          recent_activities=recent_activities)

@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login route"""
    # Redirect if already logged in as admin
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.find_by_username(username)
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            flash('Admin login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Admin login failed. Please check your credentials.', 'danger')
    
    return render_template('login.html', title='Admin Login')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout route"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard route"""
    # Mock statistics for the dashboard
    stats = {
        'user_count': User.query.count(),
        'activity_count': 0,  # Placeholder for future implementation
        'park_count': 0,      # Placeholder for future implementation
        'total_points': User.query.with_entities(db.func.sum(User.points)).scalar() or 0
    }
    
    return render_template('admin_dashboard.html',
                          title='Admin Dashboard',
                          current_user=current_user,
                          stats=stats,
                          recent_activities=[])  # Placeholder for future implementation

def init_db():
    """Initialize the database and create tables"""
    with app.app_context():
        try:
            db.create_all()  # Create database tables
            print("Database tables created successfully")
            create_admin_if_not_exists()  # Create admin user if needed
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            # If there's an error, wait and retry (useful for container startup timing)
            import time
            time.sleep(5)
            print("Retrying database initialization...")
            db.create_all()
            create_admin_if_not_exists()

if __name__ == '__main__':
    # Initialize database with retry logic for container startup
    init_db()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)