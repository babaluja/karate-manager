from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db

# Define belt colors as constants
BELT_COLORS = [
    "Bianca",
    "Bianca-Gialla",
    "Gialla",
    "Gialla-Arancione",
    "Arancione",
    "Arancione-Verde",
    "Verde",
    "Verde-Blu",
    "Blu",
    "Blu-Marrone",
    "Marrone",
    "Nera 1° Dan",
    "Nera 2° Dan",
    "Nera 3° Dan",
    "Nera 4° Dan",
    "Nera 5° Dan"
]

class Athlete(db.Model):
    """Model for karate athletes"""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    belt_color = db.Column(db.String(20), nullable=False, default="Bianca")
    enrollment_date = db.Column(db.Date, default=datetime.now().date)
    monthly_fee = db.Column(db.Float, default=0)  # Quota mensile in euro
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    payments = db.relationship('Payment', backref='athlete', lazy=True, cascade="all, delete-orphan")
    exams = db.relationship('Exam', backref='athlete', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Athlete {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Payment(db.Model):
    """Model for monthly payments"""
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    month = db.Column(db.Integer, nullable=False)  # 1-12 for Jan-Dec
    year = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), default="Cash")  # Cash, Bank Transfer, etc.
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.amount}€ - {self.month}/{self.year}>"


class Exam(db.Model):
    """Model for belt exams"""
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    previous_belt = db.Column(db.String(20), nullable=False)
    new_belt = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(20), default="Passed")  # Passed, Failed, Pending
    fee = db.Column(db.Float, nullable=False, default=0.0)
    paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f"<Exam {self.id} - {self.previous_belt} to {self.new_belt}>"


class User(UserMixin, db.Model):
    """Model for user authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(256))
    pin_hash = db.Column(db.String(256))  # Per autenticazione rapida con PIN numerico
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        """Imposta un PIN numerico per accesso rapido"""
        self.pin_hash = generate_password_hash(pin)
        
    def check_pin(self, pin):
        """Verifica il PIN numerico per accesso rapido"""
        return check_password_hash(self.pin_hash, pin)
    
    def __repr__(self):
        return f"<User {self.username or self.email}>"
