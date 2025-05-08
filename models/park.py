from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Park(db.Model):
    """Park model for storing Indianapolis park locations"""
    __tablename__ = "parks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    facilities = db.Column(db.Text)  # Comma-separated list of facilities
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Park {self.name}>'
    
    @classmethod
    def get_all_parks(cls):
        """Get all parks ordered by name"""
        return cls.query.order_by(cls.name).all()
    
    @classmethod
    def find_by_id(cls, park_id):
        """Find park by ID"""
        return cls.query.get(park_id)
    
    @classmethod
    def find_by_name(cls, name):
        """Find park by name"""
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
    
    @classmethod
    def create_park(cls, name, address, description=None, facilities=None, 
                   latitude=None, longitude=None, image_url=None):
        """Create a new park"""
        park = cls(
            name=name,
            address=address,
            description=description,
            facilities=facilities,
            latitude=latitude,
            longitude=longitude,
            image_url=image_url
        )
        db.session.add(park)
        db.session.commit()
        return park
    
    def get_facility_list(self):
        """Return facilities as a list"""
        if not self.facilities:
            return []
        return [facility.strip() for facility in self.facilities.split(',')]
    
    def to_dict(self):
        """Convert park to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'description': self.description,
            'facilities': self.get_facility_list(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image_url': self.image_url
        }