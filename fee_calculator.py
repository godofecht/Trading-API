from math import ceil
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Make sure to install python-dateutil if not already available

class FeeCalculator:
    def __init__(self, client_fee_rate):
        self.client_fee_rate = client_fee_rate  # Annualized fee rate for the client

    def calculate_fee(self, buy_price, months_held):
        """
        Calculate the fee for a given buy price and holding period.
        
        Formula: Sell Price = Buy Price * (1 + Fee Rate / 12) ^ Months Held
        """
        return buy_price * ((1 + (self.client_fee_rate / 12)) ** months_held)

    def calculate_total_fee_and_apply_fifo(self, buy_orders, sell_quantity, session):
        """
        Calculate the total fee for a sell order and apply FIFO to deplete the stock.
        
        :param buy_orders: List of buy orders for the product (FIFO order)
        :param sell_quantity: Quantity to sell in this transaction
        :param session: Active database session for making changes to orders
        :return: Total fee for the sell transaction
        """
        remaining_quantity = sell_quantity
        total_fee = 0

        try:
            for buy_order in buy_orders:
                if remaining_quantity <= 0:
                    break

                # Calculate how many months the product was held
                time_difference = relativedelta(datetime.utcnow(), buy_order.timestamp)
                months_held = time_difference.years * 12 + time_difference.months + (1 if time_difference.days > 0 else 0)

                # Calculate the fee for this portion of the stock
                fee_per_unit = self.calculate_fee(buy_order.price, months_held)

                # Determine how much we can sell from this particular buy order
                quantity_to_sell = min(remaining_quantity, buy_order.quantity)

                # Update the remaining quantity to sell
                remaining_quantity -= quantity_to_sell

                # Accumulate the total fee based on quantity sold from this buy order
                total_fee += quantity_to_sell * fee_per_unit

                # Apply FIFO: Update or delete the buy order based on how much is left
                if buy_order.quantity == quantity_to_sell:  # This order is fully depleted
                    session.delete(buy_order)
                else:  # Partially sell from this order
                    buy_order.quantity -= quantity_to_sell
                    session.add(buy_order)

            # Commit the transaction to save changes to the buy orders
            session.commit()

        except Exception as e:
            # Rollback the transaction if any error occurs
            session.rollback()
            raise e

        return total_fee
