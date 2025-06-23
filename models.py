from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='customer')
    orders = db.relationship('Order', backref='customer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price_per_kg = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<Service {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    pickup_datetime = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    weight = db.Column(db.Float)
    total_price = db.Column(db.Float)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship('Service', backref='orders', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)
    
    # Property untuk mendapatkan payment utama
    @property
    def payment(self):
        return self.payments[0] if self.payments else None

    def __repr__(self):
        return f'<Order {self.id}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.id}>'