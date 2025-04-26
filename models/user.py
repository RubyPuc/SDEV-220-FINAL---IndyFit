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