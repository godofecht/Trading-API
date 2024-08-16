# utils.py
from sqlalchemy import func
from models import Order
from datetime import datetime
from math import ceil

def calculate_balance(client_id, date=None):
    query = db.session.query(
        Order.product_id,
        func.sum(Order.quantity).label('total_quantity')
    ).filter_by(client_id=client_id)
    
    if date:
        query = query.filter(Order.timestamp <= date)
    
    query = query.group_by(Order.product_id)
    
    return query.all()

def calculate_product_balance(product_id, date=None):
    query = db.session.query(
        Order.client_id,
        func.sum(Order.quantity).label('total_quantity')
    ).filter_by(product_id=product_id)
    
    if date:
        query = query.filter(Order.timestamp <= date)
    
    query = query.group_by(Order.client_id)
    
    return query.all()
