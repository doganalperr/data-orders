import pandas as pd
from olist.data import Olist


class Order:
    def __init__(self):
        self.data = Olist().get_data()

    def get_wait_time(self):
        orders = self.data["orders"].copy()

        # 1️⃣ delivered siparişler
        orders = orders[orders["order_status"] == "delivered"]

        # 2️⃣ datetime dönüşümleri
        date_cols = [
            "order_purchase_timestamp",
            "order_delivered_customer_date",
            "order_estimated_delivery_date"
        ]

        for col in date_cols:
            orders[col] = pd.to_datetime(orders[col])

        # 3️⃣ wait_time
        orders["wait_time"] = (
            orders["order_delivered_customer_date"]
            - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        # 4️⃣ expected_wait_time
        orders["expected_wait_time"] = (
            orders["order_estimated_delivery_date"]
            - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        # 5️⃣ delay_vs_expected
        orders["delay_vs_expected"] = (
            orders["wait_time"] - orders["expected_wait_time"]
        ).clip(lower=0)

        # 6️⃣ index
        orders = orders.set_index("order_id")

        return orders[
            ["wait_time", "expected_wait_time", "delay_vs_expected"]
        ]
