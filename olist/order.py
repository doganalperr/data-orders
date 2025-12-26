import pandas as pd
from olist.data import Olist


class Order:
    def __init__(self):
        self.data = Olist().get_data()

    def get_wait_time(self):
        orders = self.data["orders"].copy()
        reviews = self.data["order_reviews"].copy()

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

        # 3️⃣ wait_time (gün, float)
        orders["wait_time"] = (
            orders["order_delivered_customer_date"]
            - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        # 4️⃣ expected_wait_time (gün, float)
        orders["expected_wait_time"] = (
            orders["order_estimated_delivery_date"]
            - orders["order_purchase_timestamp"]
        ).dt.total_seconds() / (24 * 3600)

        # 5️⃣ delay_vs_expected
        orders["delay_vs_expected"] = (
            orders["wait_time"] - orders["expected_wait_time"]
        ).clip(lower=0)

        # 6️⃣ REVIEWS'U ORDER LEVEL'A İNDİR (ÇOK KRİTİK)
        reviews = (
            reviews
            .groupby("order_id", as_index=False)
            .agg({"review_score": "mean"})
        )

        # 7️⃣ merge (artık satır sayısı bozulmaz)
        orders = orders.merge(
            reviews,
            on="order_id",
            how="left"
        )

        # 8️⃣ Testin beklediği kolonlar
        return orders[[
            "order_id",
            "wait_time",
            "expected_wait_time",
            "delay_vs_expected",
            "review_score"
        ]]



    def get_review_score(self):
        reviews = self.data["order_reviews"].copy()
        reviews["dim_is_five_star"] = reviews["review_score"].map(lambda x: 1 if x == 5 else 0)
        reviews["dim_is_one_star"] = reviews["review_score"].map(lambda x: 1 if x == 1 else 0)
        return reviews[["order_id", "dim_is_five_star", "dim_is_one_star", "review_score"]]
