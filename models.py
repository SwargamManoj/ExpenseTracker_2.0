import os
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(200), default='default_profile.jpg')
    
    # New profile fields
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True, default='default_profile.png')
    
    # Track additional user metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationship with expenses
    expenses = db.relationship('Expense', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_profile_picture(self, file):
        """
        Save and set profile picture with unique filename
        
        Args:
            file (FileStorage): Uploaded file object
        
        Returns:
            str: Filename of saved profile picture
        """
        if file:
            # Generate unique filename
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            
            # Ensure upload directory exists
            upload_path = os.path.join('static', 'uploads', 'profiles')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Delete old profile picture if exists (except default)
            if self.profile_picture and self.profile_picture != 'default_profile.jpg':
                old_file_path = os.path.join(upload_path, self.profile_picture)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Update profile picture filename
            self.profile_picture = filename
            return filename
        
        return self.profile_picture
    
class Expense(db.Model):
    """
    Expense model representing individual expense entries.
    
    Attributes:
        id (int): Unique identifier for the expense
        amount (float): Monetary value of the expense
        category (str): Expense category
        description (str): Optional description of the expense
        date (datetime): Timestamp of the expense entry
        user_id (int): Foreign key linking to the User model
    """
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key relationship with User model
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    @classmethod
    def get_total_expenses_by_category(cls, user_id):
        """
        Calculate total expenses for each category for a specific user.
        
        Args:
            user_id (int): ID of the user
        
        Returns:
            dict: Total expenses grouped by category
        """
        return dict(db.session.query(
            cls.category, 
            db.func.sum(cls.amount)
        ).filter(cls.user_id == user_id)
         .group_by(cls.category)
         .all())

    def __repr__(self):
        """
        String representation of the Expense model.
        
        Returns:
            str: Expense details representation
        """
        return f'<Expense {self.category}: ${self.amount}>'

# Optional utility function for database initialization
def init_db(app):
    """
    Initialize the database with the given Flask app context.
    
    Args:
        app (Flask): Flask application instance
    """
    with app.app_context():
        db.create_all()
        db.session.commit()