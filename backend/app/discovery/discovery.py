"""Discovery service — resolves a product + merchant into a concrete SKU.

For the hackathon MVP this uses a mock catalog. It can later be replaced
with real merchant discovery APIs without changing the rest of the pipeline.
"""
from typing import Optional

from ..schemas import Product

# Mock product catalog (5-10 products across allowed merchants).
PRODUCTS: list[dict] = [
    {"sku": "NIKE-AIR-001", "merchant": "Nike", "name": "Running Shoes", "price": 40.0, "currency": "XSGD"},
    {"sku": "NIKE-DRI-002", "merchant": "Nike", "name": "Dri-FIT T-Shirt", "price": 25.0, "currency": "XSGD"},
    {"sku": "NIKE-CAP-003", "merchant": "Nike", "name": "Classic Cap", "price": 20.0, "currency": "XSGD"},
    {"sku": "AMZ-ECHO-001", "merchant": "Amazon", "name": "Echo Dot", "price": 49.99, "currency": "XSGD"},
    {"sku": "AMZ-KIND-002", "merchant": "Amazon", "name": "Kindle Paperwhite", "price": 139.99, "currency": "XSGD"},
    {"sku": "AMZ-BOOK-003", "merchant": "Amazon", "name": "Best Seller Book", "price": 15.0, "currency": "XSGD"},
    {"sku": "APL-AIRP-001", "merchant": "Apple", "name": "AirPods", "price": 129.0, "currency": "XSGD"},
    {"sku": "APL-MAG-002", "merchant": "Apple", "name": "MagSafe Charger", "price": 39.0, "currency": "XSGD"},
    {"sku": "APL-CASE-003", "merchant": "Apple", "name": "iPhone Case", "price": 29.0, "currency": "XSGD"},
]


class DiscoveryService:
    """Resolves a product + merchant into a concrete catalog entry."""

    def resolve(self, product: str, merchant: str) -> Optional[Product]:
        """Return the best-matching Product, or None if not found.

        Only returns a product when the merchant is known AND at least one
        product token matches. This prevents false positives for unknown
        merchants or unrelated products.
        """
        product_lower = product.lower()
        merchant_lower = merchant.lower()

        known_merchants = {p["merchant"].lower() for p in PRODUCTS}

        # If a merchant was specified but is not in the catalog, reject.
        if merchant_lower and merchant_lower not in known_merchants:
            return None

        # Match within the merchant's catalog (or all if merchant unknown/empty).
        candidates = [p for p in PRODUCTS if p["merchant"].lower() == merchant_lower]
        if not candidates:
            candidates = PRODUCTS

        best = None
        best_score = 0
        for p in candidates:
            name = p["name"].lower()
            score = 0
            for token in product_lower.split():
                if len(token) >= 3 and token in name:
                    score += 1
            if score > best_score:
                best_score = score
                best = p

        # Require at least one real token match.
        if best is None or best_score == 0:
            return None

        return Product(
            sku=best["sku"],
            merchant=best["merchant"],
            name=best["name"],
            price=best["price"],
            currency=best["currency"],
            checkout_url=f"https://checkout.example.com/{best['sku'].lower()}",
        )


discovery = DiscoveryService()