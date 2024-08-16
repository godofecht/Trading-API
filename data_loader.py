import json
from app import app, db
from models import Client, Product, Order
from datetime import datetime
from dateutil import parser  # Importing dateutil.parser to handle ISO 8601 format with Z

class DataLoader:
    def __init__(self, client_file, product_file, order_file):
        self.client_file = client_file
        self.product_file = product_file
        self.order_file = order_file

    def load_initial_data(self):
        with app.app_context():
            # Clear existing data
            db.drop_all()
            db.create_all()
            
            # Load clients data
            with open(self.client_file, 'r') as f:
                clients_data = json.load(f)
                for client in clients_data:
                    db.session.add(Client(
                        client_id=client['clientId'],
                        fee_rate=client['fee_rate']
                    ))

            # Load products data
            with open(self.product_file, 'r') as f:
                products_data = json.load(f)
                for product in products_data:
                    db.session.add(Product(
                        product_id=product['productId'],
                        price=product['price']
                    ))

            # Load orders data
            with open(self.order_file, 'r') as f:
                orders_data = json.load(f)
                for order in orders_data:
                    # Use dateutil.parser to handle ISO 8601 format with Z suffix
                    db.session.add(Order(
                        client_id=order['clientId'],
                        product_id=order['productId'],
                        order_type=order['type'],
                        quantity=order['quantity'],
                        price=order['price'],
                        timestamp=parser.isoparse(order['timestamp'])  # Handling the ISO 8601 format correctly
                    ))

            db.session.commit()
