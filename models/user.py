from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, UserMixin):
    """User model for storing user related details"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def add_points(self, points):
        """Add points to user's total"""
        self.points += points
        db.session.commit()
        return self.points
    
    def set_password(self, password):
        """Hash password before storing in database"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as a unicode string"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated"""
        return True
    
    @property
    def is_active(self):
        """Return True if user is active"""
        return True
    
    @property
    def is_anonymous(self):
        """Return False as anonymous users aren't supported"""
        return False
    
    @classmethod
    def create_admin_user(cls, username, email, password, first_name="Admin", last_name="User"):
        """Create an admin user"""
        admin = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=True
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin
    
    @classmethod
    def get_admin_count(cls):
        """Get count of admin users"""
        return cls.query.filter_by(is_admin=True).count()
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def create_user(cls, username, email, password, first_name, last_name):
        """Create a regular user"""
        user = cls(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            points=0
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_user_ranking(cls, user_id):
        """Get user ranking based on points"""
        # Get all users ordered by points in descending order
        users = cls.query.order_by(cls.points.desc()).all()
        
        # Find the position of the user in the list
        for i, user in enumerate(users):
            if user.id == user_id:
                return i + 1  # +1 because ranking starts at 1, not 0
        
        return len(users)  # If user not found, return last position
    
    @classmethod
    def get_leaderboard(cls, limit=10):
        """Get top users for leaderboard"""
        return cls.query.order_by(cls.points.desc()).limit(limit).all()
    
    def get_recent_activities(self, limit=5):
        """Get user's recent activities"""
        from models.activity import UserActivity
        return UserActivity.get_user_activities(self.id, limit)
    
    def get_total_activity_minutes(self):
        """Get total minutes of activities"""
        from models.activity import UserActivity
        result = db.session.query(db.func.sum(UserActivity.duration_minutes)) \
            .filter(UserActivity.user_id == self.id) \
            .scalar()
        return result or 0
    
    def get_activity_stats(self):
        """Get statistics about user activities"""
        from models.activity import UserActivity, ActivityType
        
        # Get total activities
        total_activities = UserActivity.query.filter_by(user_id=self.id).count()
        
        # Get total minutes
        total_minutes = self.get_total_activity_minutes()
        
        # Get activity breakdown by type
        activity_breakdown = db.session.query(
            ActivityType.name,
            db.func.sum(UserActivity.duration_minutes).label('total_minutes'),
            db.func.count(UserActivity.id).label('count')
        ).join(UserActivity, UserActivity.activity_type_id == ActivityType.id) \
         .filter(UserActivity.user_id == self.id) \
         .group_by(ActivityType.name) \
         .all()
        
        return {
            'total_activities': total_activities,
            'total_minutes': total_minutes,
            'activity_breakdown': [
                {'name': name, 'minutes': minutes, 'count': count}
                for name, minutes, count in activity_breakdown
            ]
        }