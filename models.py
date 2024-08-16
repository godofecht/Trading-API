# models.py
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # Import datetime

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), unique=True, nullable=False)
    fee_rate = db.Column(db.Float, nullable=False)  # Annualized fee rate

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Predetermined price

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(80), db.ForeignKey('client.client_id'), nullable=False)
    product_id = db.Column(db.String(80), db.ForeignKey('product.product_id'), nullable=False)
    order_type = db.Column(db.String(4), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
