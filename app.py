from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from datetime import datetime
from functools import wraps
from models import db, bcrypt, User, Park, ActivityType, UserActivity

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
    # Get real activity data
    recent_activities = current_user.get_recent_activities(5)
    activities_count = len(recent_activities)
    ranking = User.get_user_ranking(current_user.id)
    activity_stats = current_user.get_activity_stats()
    
    return render_template('profile.html',
                          title='My Profile',
                          current_user=current_user,
                          activities_count=activities_count,
                          ranking=ranking,
                          recent_activities=recent_activities,
                          activity_stats=activity_stats)

@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Activity tracking routes
@app.route('/activities', methods=['GET', 'POST'])
@login_required
def activities():
    """Activity tracking route"""
    # Get all activity types and parks for the form
    activity_types = ActivityType.get_all_types()
    parks = Park.get_all_parks()
    
    if request.method == 'POST':
        activity_type_id = request.form.get('activity_type_id')
        park_id = request.form.get('park_id')
        duration_minutes = request.form.get('duration_minutes')
        date_str = request.form.get('date')
        notes = request.form.get('notes')
        
        # Validate form data
        if not activity_type_id or not park_id or not duration_minutes:
            flash('Please fill in all required fields.', 'danger')
            return render_template('activities.html',
                                  title='Log Activity',
                                  activity_types=activity_types,
                                  parks=parks)
        
        try:
            # Parse date or use today
            activity_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.utcnow().date()
            
            # Create activity
            activity = UserActivity.create_activity(
                user_id=current_user.id,
                activity_type_id=int(activity_type_id),
                park_id=int(park_id),
                duration_minutes=int(duration_minutes),
                notes=notes,
                date=activity_date
            )
            
            flash(f'Activity logged successfully! You earned {activity.points_earned} points.', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'Error logging activity: {str(e)}', 'danger')
    
    # GET request - show form
    return render_template('activities.html',
                          title='Log Activity',
                          activity_types=activity_types,
                          parks=parks,
                          today=datetime.utcnow().date().strftime('%Y-%m-%d'))

@app.route('/parks')
def parks_list():
    """Parks listing route"""
    parks = Park.get_all_parks()
    return render_template('parks.html',
                          title='Indianapolis Parks',
                          parks=parks)

@app.route('/parks/<int:park_id>')
def park_detail(park_id):
    """Park detail route"""
    park = Park.find_by_id(park_id)
    if not park:
        flash('Park not found.', 'danger')
        return redirect(url_for('parks_list'))
    
    # Get recent activities at this park
    recent_activities = UserActivity.get_park_activities(park_id)
    
    return render_template('park_detail.html',
                          title=park.name,
                          park=park,
                          recent_activities=recent_activities)

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard route"""
    top_users = User.get_leaderboard(20)
    return render_template('leaderboard.html',
                          title='Leaderboard',
                          top_users=top_users,
                          current_user=current_user if current_user.is_authenticated else None)

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
    # Real statistics for the dashboard
    stats = {
        'user_count': User.query.count(),
        'activity_count': UserActivity.query.count(),
        'park_count': Park.query.count(),
        'total_points': User.query.with_entities(db.func.sum(User.points)).scalar() or 0
    }
    
    return render_template('admin_dashboard.html',
                          title='Admin Dashboard',
                          current_user=current_user,
                          stats=stats,
                          recent_activities=UserActivity.get_recent_activities(10))

def init_db():
    """Initialize the database and create tables"""
    with app.app_context():
        try:
            db.create_all()  # Create database tables
            print("Database tables created successfully")
            create_admin_if_not_exists()  # Create admin user if needed
            create_default_data()  # Create default activity types and parks
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            # If there's an error, wait and retry (useful for container startup timing)
            import time
            time.sleep(5)
            print("Retrying database initialization...")
            db.create_all()
            create_admin_if_not_exists()
            create_default_data()

def create_default_data():
    """Create default activity types and parks if they don't exist"""
    # Create default activity types
    if ActivityType.query.count() == 0:
        print("Creating default activity types...")
        default_activities = [
            {"name": "Walking", "description": "A casual walk in the park", "points_per_minute": 1, "icon": "fa-walking"},
            {"name": "Running", "description": "Jogging or running", "points_per_minute": 2, "icon": "fa-running"},
            {"name": "Cycling", "description": "Biking on trails or paths", "points_per_minute": 2, "icon": "fa-bicycle"},
            {"name": "Hiking", "description": "Hiking on nature trails", "points_per_minute": 3, "icon": "fa-hiking"},
            {"name": "Swimming", "description": "Swimming in pools or lakes", "points_per_minute": 3, "icon": "fa-swimmer"},
            {"name": "Yoga", "description": "Outdoor yoga sessions", "points_per_minute": 2, "icon": "fa-pray"},
            {"name": "Basketball", "description": "Playing basketball", "points_per_minute": 3, "icon": "fa-basketball-ball"},
            {"name": "Tennis", "description": "Playing tennis", "points_per_minute": 3, "icon": "fa-table-tennis"}
        ]
        
        for activity in default_activities:
            ActivityType.create_activity_type(**activity)
        print(f"Created {len(default_activities)} default activity types")
    
    # Create default parks
    if Park.query.count() == 0:
        print("Creating default parks...")
        default_parks = [
            {
                "name": "Eagle Creek Park",
                "address": "7840 W 56th St, Indianapolis, IN 46254",
                "description": "One of the largest municipal parks in the United States with over 3,900 acres of land and 1,400 acres of water.",
                "facilities": "Hiking trails, Fishing, Boating, Swimming, Bird watching, Picnic areas",
                "latitude": 39.8352,
                "longitude": -86.3077,
                "image_url": "https://example.com/eagle_creek.jpg"
            },
            {
                "name": "Garfield Park",
                "address": "2345 Pagoda Dr, Indianapolis, IN 46203",
                "description": "Oldest city park in Indianapolis featuring a conservatory and sunken gardens.",
                "facilities": "Conservatory, Sunken gardens, Arts center, Aquatic center, Picnic areas",
                "latitude": 39.7329,
                "longitude": -86.1443,
                "image_url": "https://example.com/garfield_park.jpg"
            },
            {
                "name": "Holliday Park",
                "address": "6363 Spring Mill Rd, Indianapolis, IN 46260",
                "description": "94-acre park featuring The Ruins, nature center, and hiking trails.",
                "facilities": "Playground, Nature center, Hiking trails, Picnic areas",
                "latitude": 39.8719,
                "longitude": -86.1694,
                "image_url": "https://example.com/holliday_park.jpg"
            }
        ]
        
        for park in default_parks:
            Park.create_park(**park)
        print(f"Created {len(default_parks)} default parks")

if __name__ == '__main__':
    # Initialize database with retry logic for container startup
    init_db()
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)