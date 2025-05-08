# Import all models to make them available when importing from the models package
from models.user import User, db, bcrypt
from models.park import Park
from models.activity import ActivityType, UserActivity

# Export all models
__all__ = ['User', 'Park', 'ActivityType', 'UserActivity', 'db', 'bcrypt']