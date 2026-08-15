"""Payment Agent — converts natural language into a structured purchase intent.

The LLM is used ONLY for intent extraction. It never controls funds directly.
The output is a structured Intent that flows through the policy engine.
"""
import json
import re
from typing import Optional

from ..config import settings
from ..schemas import Intent


class PaymentAgent:
    """Parses a user message into a structured purchase Intent."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.agent_provider

    def understand_intent(self, user_message: str) -> Intent:
        """Return a structured Intent for the given natural language message."""
        if self.provider == "openai" and settings.openai_api_key:
            try:
                return self._openai_intent(user_message)
            except Exception:
                # Fall back to the rule-based parser on any LLM failure.
                return self._mock_intent(user_message)
        return self._mock_intent(user_message)

    # --- OpenAI provider ---
    def _openai_intent(self, user_message: str) -> Intent:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)

        system_prompt = (
            "You extract purchase intents from natural language. "
            "Return ONLY a JSON object with keys: "
            "action, product, merchant, max_amount, currency. "
            "action is always 'purchase'. currency is always 'XSGD'. "
            "max_amount is a number. If the amount is ambiguous, use 0."
        )

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        return Intent(
            action=data.get("action", "purchase"),
            product=data.get("product", ""),
            merchant=data.get("merchant", ""),
            max_amount=float(data.get("max_amount", 0)),
            currency=data.get("currency", "XSGD"),
        )

    # --- Rule-based fallback ---
    def _mock_intent(self, user_message: str) -> Intent:
        text = user_message.lower()

        # Extract amount: "$40", "40 dollars", "40 xsgd"
        amount = 0.0
        amount_match = re.search(r"\$?\s*(\d+(?:\.\d+)?)\s*(?:usd|dollars|xsgd|sgd)?", text)
        if amount_match:
            amount = float(amount_match.group(1))

        # Known merchants
        merchant = ""
        for known in ["nike", "amazon", "apple"]:
            if known in text:
                merchant = known.capitalize()
                break

        # Product: strip leading verbs and merchant/amount words (word-boundary safe)
        product = text
        for word in ["buy", "purchase", "order", "get", "please", "for", "i want", "a", "an", "the"]:
            product = re.sub(rf"\b{re.escape(word)}\b", " ", product)
        product = re.sub(r"\$?\s*\d+(?:\.\d+)?\s*(?:usd|dollars|xsgd|sgd)?", " ", product)
        product = re.sub(r"\b(nike|amazon|apple)\b", " ", product)
        product = re.sub(r"\s+", " ", product).strip().title()

        return Intent(
            action="purchase",
            product=product or "Unknown Product",
            merchant=merchant or "Unknown Merchant",
            max_amount=amount,
            currency="XSGD",
        )


agent = PaymentAgent()