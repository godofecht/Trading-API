You looking for a guy in finance?

# Trading-API

This project implements a simple trading API built using Flask and SQLAlchemy. The API allows clients to interact with products, place buy/sell orders, and track their portfolio and product balances over time. The API also supports transaction logging, fee calculations, and retrieving various metrics.

## Features

- **Client Management**: Keep track of client data including orders and transactions.
- **Product Management**: Manage products available for trading.
- **Order Management**: Record buy and sell orders for products by clients.
- **Portfolio Metrics**: Calculate key portfolio metrics including life-to-date fee notional, outstanding fee notional, and weighted average yield.
- **Transaction Tracking**: Retrieve historical transactions for clients and products.
- **Testing**: Includes automated tests for various endpoints.

## Endpoints

### 1. `/balance/client/<client_id>` [GET]

Retrieve the balance of a specific client, showing the quantity of products they currently hold.

**Query Parameters:**
- `date` (optional): Retrieve the balance as of a specific date.

**Example Request:**
```bash
GET /balance/client/C-1
```

**Example Response:**
```json
[
    {"clientId": "C-1", "productId": "P-1", "quantity": 850},
    {"clientId": "C-1", "productId": "P-2", "quantity": 1}
]
```

### 2. `/balance/product/<product_id>` [GET]

Retrieve the balance of a specific product, showing the quantity of products held by each client.

**Example Request:**
```bash
GET /balance/product/P-1
```

**Example Response:**
```json
[
    {"clientId": "C-1", "productId": "P-1", "quantity": 850}
]
```

### 3. `/portfolio/client/<client_id>` [GET]

Retrieve portfolio metrics for a specific client including life-to-date fee notional, outstanding fee notional, and other key statistics.

**Query Parameters:**
- `date` (optional): Retrieve the portfolio metrics as of a specific date.

**Example Request:**
```bash
GET /portfolio/client/C-1?date=2024-01-01
```

**Example Response:**
```json
{
    "lifeToDateFeeNotional": 13339.69,
    "lifeToDateProductNotional": 659900,
    "outstandingFeeNotional": 154573.73,
    "outstandingProductNotional": 40751.18,
    "weightedAverageRealisedAnnualisedYield": 11416.76,
    "weightedAverageRealisedDuration": 327.30
}
```

### 4. `/transactions/client/<client_id>` [GET]

Retrieve all transactions for a specific client.

**Example Request:**
```bash
GET /transactions/client/C-1
```

**Example Response:**
```json
[
    {
        "clientId": "C-1",
        "productId": "P-1",
        "orderType": "buy",
        "quantity": 1000,
        "price": 47.90,
        "timestamp": "2020-01-01T10:00:00Z"
    },
    ...
]
```

### 5. `/transactions/product/<product_id>` [GET]

Retrieve all transactions for a specific product.

**Example Request:**
```bash
GET /transactions/product/P-1
```

**Example Response:**
```json
[
    {
        "clientId": "C-1",
        "productId": "P-1",
        "orderType": "buy",
        "quantity": 1000,
        "price": 47.90,
        "timestamp": "2020-01-01T10:00:00Z"
    },
    ...
]
```

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/godofecht/trading-api.git
   cd trading-api
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   flask db upgrade
   ```

5. **Run the Application**
   ```bash
   flask run
   ```

## Testing

This project includes a test suite built using `pytest` that tests various API endpoints and the database models.

To run the tests, simply execute:
```bash
pytest
```

## Logging

Logging is configured to provide detailed information during testing and debugging. To view logs, ensure the log level is set appropriately in your environment.

## Project Structure

```plaintext
Trading-API/
│
├── app.py                # Main application entry point
├── models.py             # Database models for Client, Product, and Order
├── data_loader.py        # Utility to load initial data into the database
├── fee_calculator.py     # Logic for calculating fees
├── tests/
│   ├── test_models.py    # Tests for models
│   ├── test_api.py       # Tests for API endpoints
├── clients.json          # Sample data for clients
├── products.json         # Sample data for products
├── orders.json           # Sample data for orders
├── README.md             # Project documentation
├── requirements.txt      # Project dependencies
└── ...
```

## Contributing

If you wish to contribute to this project, feel free to submit a pull request. Ensure that any changes are accompanied by corresponding test cases and that the full test suite passes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Happy Trading! 🎉
