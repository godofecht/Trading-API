import json
from flask import Flask, jsonify, request
from models import db, Client, Product, Order
from database import init_db
from datetime import datetime
from fee_calculator import FeeCalculator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize the database
with app.app_context():
    init_db()

@app.route('/balance/client/<client_id>', methods=['GET'])
def get_client_balance(client_id):
    client_orders = db.session.query(Order).filter_by(client_id=client_id).all()
    product_quantities = {}

    for order in client_orders:
        if order.order_type == 'buy':
            product_quantities[order.product_id] = product_quantities.get(order.product_id, 0) + order.quantity
        elif order.order_type == 'sell':
            product_quantities[order.product_id] = product_quantities.get(order.product_id, 0) - order.quantity
            if product_quantities[order.product_id] <= 0:
                product_quantities[order.product_id] = 0

    result = [{"clientId": client_id, "productId": product_id, "quantity": quantity}
              for product_id, quantity in product_quantities.items() if quantity > 0]
    return jsonify(result), 200

def parse_date(date_str):
    """Helper function to parse date string."""
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None
    return None

import json
import pytest
import logging
from app import app, db, Client, Product, Order
from datetime import datetime
from fee_calculator import FeeCalculator
from data_loader import DataLoader

# Setup logging
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        with app.test_client() as testing_client:
            yield testing_client
        db.drop_all()

@pytest.fixture(scope='module')
def setup_data():
    loader = DataLoader('clients.json', 'products.json', 'orders.json')
    with app.app_context():
        loader.load_initial_data()  # Load initial data for tests
        yield
        # Clean up
        db.drop_all()

@pytest.mark.usefixtures('setup_data')
def test_models_creation(test_client):
    """Test to ensure that models are created and data is loaded into the database."""
    with app.app_context():
        logging.debug("Testing model creation and data loading...")
        assert db.session.query(Client).count() == 3  # Now expecting 3 clients
        assert db.session.query(Product).count() == 3  # Now expecting 3 products
        assert db.session.query(Order).count() == 12  # Now expecting 12 orders

        client1 = db.session.query(Client).filter_by(client_id='C-1').first()
        assert client1 is not None
        assert client1.fee_rate == 0.01

@pytest.mark.usefixtures('setup_data')
def test_get_client_balance(test_client):
    response = test_client.get('/balance/client/C-1')
    data = response.get_json()
    logging.debug(f"Client C-1 balance response: {data}")

    expected = [
        {"clientId": "C-1", "productId": "P-1", "quantity": 850},
        {"clientId": "C-1", "productId": "P-2", "quantity": 1}
    ]

    assert response.status_code == 200
    assert data == expected

    response = test_client.get('/balance/client/C-1?date=2020-01-15')
    data = response.get_json()
    logging.debug(f"Client C-1 balance snapshot on 2020-01-15: {data}")

    expected_snapshot = [
        {"clientId": "C-1", "productId": "P-1", "quantity": 850},
        {"clientId": "C-1", "productId": "P-2", "quantity": 1}
    ]
    
    print(data)
    
    assert data == expected_snapshot

@app.route('/balance/product/<product_id>', methods=['GET'])
def get_product_balance(product_id):
    # Fetch all orders related to the product, ordered by timestamp
    product_orders = db.session.query(Order).filter_by(product_id=product_id).order_by(Order.timestamp).all()
    client_quantities = {}

    # Process each order to compute the final balances
    for order in product_orders:
        logging.debug(f"Processing order: {order}")
        
        if order.order_type == 'buy':
            client_quantities[order.client_id] = client_quantities.get(order.client_id, 0) + order.quantity
            logging.debug(f"After buy: {client_quantities[order.client_id]} units for client {order.client_id}")
        elif order.order_type == 'sell':
            if order.client_id in client_quantities:
                client_quantities[order.client_id] -= order.quantity
                logging.debug(f"After sell: {client_quantities[order.client_id]} units for client {order.client_id}")

            # Ensure the quantity does not go negative
            if client_quantities[order.client_id] < 0:
                client_quantities[order.client_id] = 0
                logging.debug(f"Corrected to zero units for client {order.client_id}")

    # Only include clients with a positive quantity in the result
    result = [{"clientId": client_id, "productId": product_id, "quantity": quantity}
              for client_id, quantity in client_quantities.items() if quantity > 0]

    logging.debug(f"Final result: {result}")
    return jsonify(result), 200

@pytest.mark.usefixtures('setup_data')
def test_get_portfolio_metrics(test_client):
    response = test_client.get('/portfolio/client/C-1?date=2024-01-01')
    data = response.get_json()
    logging.debug(f"Portfolio metrics for client C-1: {data}")

    expected = {
        "lifeToDateFeeNotional": pytest.approx(13339.69, 0.01),
        "lifeToDateProductNotional": pytest.approx(659900, 0.01),
        "outstandingFeeNotional": pytest.approx(154573.73, 0.01),
        "outstandingProductNotional": pytest.approx(40751.18, 0.01),
        "weightedAverageRealisedAnnualisedYield": pytest.approx(11416.76, 0.01),
        "weightedAverageRealisedDuration": pytest.approx(327.30, 0.01)
    }

    assert response.status_code == 200
    assert data == expected

@pytest.mark.usefixtures('setup_data')
def test_get_client_transactions(test_client):
    response = test_client.get('/transactions/client/C-1')
    data = response.get_json()
    logging.debug(f"Transactions for client C-1: {data}")

    assert response.status_code == 200
    assert len(data) == 6  # Expecting 6 transactions for client C-1
    assert data[0]['clientId'] == 'C-1'
    assert data[0]['productId'] == 'P-1'
    assert data[0]['orderType'] == 'buy'

@pytest.mark.usefixtures('setup_data')
def test_get_product_transactions(test_client):
    response = test_client.get('/transactions/product/P-1')
    data = response.get_json()
    logging.debug(f"Transactions for product P-1: {data}")

    assert response.status_code == 200
    assert len(data) == 6  # Expecting 6 transactions for product P-1
    assert data[0]['productId'] == 'P-1'
    assert data[0]['clientId'] == 'C-1'

@app.route('/portfolio/client/<client_id>', methods=['GET'])
def get_portfolio_metrics(client_id):
    # Parse the date query parameter
    date_str = request.args.get('date')
    query_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()

    # Query for the client's transactions up to the specified date
    transactions = db.session.query(Order).filter(Order.client_id == client_id, Order.timestamp <= query_date).all()

    # Initialize the metric variables
    life_to_date_fee_notional = 0
    life_to_date_product_notional = 0
    outstanding_fee_notional = 0
    outstanding_product_notional = 0
    weighted_yield_sum = 0
    weighted_duration_sum = 0
    total_weight = 0
    
    # Track the remaining quantities of products
    product_positions = {}

    # Store purchase timestamps and prices for yield calculations
    purchase_records = {}

    # Process each transaction
    for transaction in transactions:
        quantity = transaction.quantity
        price = transaction.price
        product_id = transaction.product_id
        timestamp = transaction.timestamp

        if transaction.order_type == 'buy':
            # Add bought quantities to the positions
            if product_id in product_positions:
                product_positions[product_id] += quantity
            else:
                product_positions[product_id] = quantity

            # Add to life to date product notional (total value of purchases)
            life_to_date_product_notional += quantity * price

            # Record the purchase price and timestamp
            purchase_records[product_id] = {
                "price": price,
                "timestamp": timestamp
            }

        elif transaction.order_type == 'sell':
            # The quantity sold
            units_sold = quantity

            if product_id in product_positions:
                previous_quantity = product_positions[product_id]
                product_positions[product_id] -= units_sold

                # Calculate the fee for the sell
                life_to_date_fee_notional += units_sold * price * 0.10  # Fee based on 10% of sale price

                # Calculate realised yield and duration for the sold quantity
                if product_id in purchase_records:
                    buy_price = purchase_records[product_id]["price"]
                    buy_timestamp = purchase_records[product_id]["timestamp"]
                    
                    # Calculate holding period in years
                    holding_period_years = (timestamp - buy_timestamp).days
                    
                    # Calculate yield percentage and annualized yield
                    yield_perc = (price - buy_price) / buy_price
                    annualized_yield = (1 + yield_perc) ** (1 / holding_period_years) - 1 if holding_period_years > 0 else 0

                    # Weight calculations for yield and duration
                    weight = units_sold * buy_price
                    weighted_yield_sum += annualized_yield * weight
                    weighted_duration_sum += holding_period_years * weight
                    total_weight += weight

    # Calculate outstanding product notional and fee notional
    for product_id, remaining_quantity in product_positions.items():
        if remaining_quantity > 0:
            latest_price = purchase_records[product_id]["price"]
            outstanding_fee_notional += remaining_quantity * latest_price# * 0.10  # Fee based on 10% of remaining inventory value
            outstanding_product_notional += remaining_quantity * latest_price

    # Calculate weighted averages
    weighted_average_yield = weighted_yield_sum / total_weight if total_weight > 0 else 0
    weighted_average_duration = weighted_duration_sum / total_weight if total_weight > 0 else 0

    # Prepare the final result
    metrics = {
        "lifeToDateFeeNotional": life_to_date_fee_notional,
        "lifeToDateProductNotional": life_to_date_product_notional,
        "outstandingFeeNotional": outstanding_fee_notional,  # Removed the unnecessary scaling
        "outstandingProductNotional": outstanding_product_notional,
        "weightedAverageRealisedAnnualisedYield": weighted_average_yield,
        "weightedAverageRealisedDuration": weighted_average_duration
    }

    return jsonify(metrics), 200



@app.route('/transactions/client/<client_id>', methods=['GET'])
def get_client_transactions(client_id):
    transactions = db.session.query(Order).filter_by(client_id=client_id).all()
    result = [
        {
            "clientId": order.client_id,
            "productId": order.product_id,
            "orderType": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "timestamp": order.timestamp.isoformat()
        }
        for order in transactions
    ]
    return jsonify(result), 200

@app.route('/transactions/product/<product_id>', methods=['GET'])
def get_product_transactions(product_id):
    transactions = db.session.query(Order).filter_by(product_id=product_id).all()
    result = [
        {
            "clientId": order.client_id,
            "productId": order.product_id,
            "orderType": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "timestamp": order.timestamp.isoformat()
        }
        for order in transactions
    ]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
