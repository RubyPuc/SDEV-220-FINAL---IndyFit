from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db, User
from models.park import Park

class ActivityType(db.Model):
    """Activity type model for categorizing different types of activities"""
    __tablename__ = "activity_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    points_per_minute = db.Column(db.Integer, default=1)  # Base points earned per minute
    icon = db.Column(db.String(50))  # CSS class or icon name
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityType {self.name}>'
    
    @classmethod
    def get_all_types(cls):
        """Get all activity types ordered by name"""
        return cls.query.order_by(cls.name).all()
    
    @classmethod
    def find_by_id(cls, type_id):
        """Find activity type by ID"""
        return cls.query.get(type_id)
    
    @classmethod
    def find_by_name(cls, name):
        """Find activity type by name"""
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
    
    @classmethod
    def create_activity_type(cls, name, description=None, points_per_minute=1, icon=None):
        """Create a new activity type"""
        activity_type = cls(
            name=name,
            description=description,
            points_per_minute=points_per_minute,
            icon=icon
        )
        db.session.add(activity_type)
        db.session.commit()
        return activity_type
    
    def calculate_points(self, duration_minutes):
        """Calculate points for a given duration"""
        return self.points_per_minute * duration_minutes
    
    def to_dict(self):
        """Convert activity type to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'points_per_minute': self.points_per_minute,
            'icon': self.icon
        }


class UserActivity(db.Model):
    """User activity model for tracking user activities at parks"""
    __tablename__ = "user_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type_id = db.Column(db.Integer, db.ForeignKey('activity_types.id'), nullable=False)
    park_id = db.Column(db.Integer, db.ForeignKey('parks.id'), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationships
    user = db.relationship('User', backref=db.backref('activities', lazy=True))
    activity_type = db.relationship('ActivityType', backref=db.backref('user_activities', lazy=True))
    park = db.relationship('Park', backref=db.backref('activities', lazy=True))

    def __repr__(self):
        return f'<UserActivity {self.id} - User {self.user_id} - {self.activity_type.name if self.activity_type else "Unknown"} at {self.park.name if self.park else "Unknown"}>'
    
    @classmethod
    def create_activity(cls, user_id, activity_type_id, park_id, duration_minutes, notes=None, date=None):
        """Create a new user activity and update user points"""
        # Get the activity type to calculate points
        activity_type = ActivityType.find_by_id(activity_type_id)
        if not activity_type:
            raise ValueError("Invalid activity type")
        
        # Calculate points earned
        points_earned = activity_type.calculate_points(duration_minutes)
        
        # Create the activity
        activity = cls(
            user_id=user_id,
            activity_type_id=activity_type_id,
            park_id=park_id,
            duration_minutes=duration_minutes,
            points_earned=points_earned,
            date=date or datetime.utcnow().date(),
            notes=notes
        )
        
        # Add the activity to the database
        db.session.add(activity)
        
        # Update user's points
        user = User.query.get(user_id)
        if user:
            user.points += points_earned
        
        # Commit the changes
        db.session.commit()
        
        return activity
    
    @classmethod
    def get_user_activities(cls, user_id, limit=10):
        """Get recent activities for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.date.desc(), cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_park_activities(cls, park_id, limit=10):
        """Get recent activities at a park"""
        return cls.query.filter_by(park_id=park_id).order_by(cls.date.desc(), cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_activities(cls, limit=20):
        """Get recent activities across all users"""
        return cls.query.order_by(cls.date.desc(), cls.created_at.desc()).limit(limit).all()
    
    def to_dict(self):
        """Convert user activity to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else "Unknown",
            'activity_type_id': self.activity_type_id,
            'activity_type_name': self.activity_type.name if self.activity_type else "Unknown",
            'park_id': self.park_id,
            'park_name': self.park.name if self.park else "Unknown",
            'duration_minutes': self.duration_minutes,
            'points_earned': self.points_earned,
            'date': self.date.strftime('%Y-%m-%d'),
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }