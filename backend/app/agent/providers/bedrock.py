"""AWS Bedrock intent provider — uses Claude via bedrock-runtime."""
import json
from typing import Optional

from ...config import settings
from ...schemas import Intent


class BedrockProvider:
    """Parse intents using AWS Bedrock (Claude)."""

    def __init__(self, region: Optional[str] = None, model_id: Optional[str] = None):
        self.region = region or settings.bedrock_region
        self.model_id = model_id or settings.bedrock_model_id

    def understand_intent(self, user_message: str) -> Intent:
        """Return a structured Intent using Bedrock Claude."""
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 is required for Bedrock provider. Install with: pip install boto3")

        client = boto3.client("bedrock-runtime", region_name=self.region)

        system_prompt = (
            "You extract purchase intents from natural language. "
            "Return ONLY a JSON object with keys: "
            "action, product, merchant, max_amount, currency. "
            "action is always 'purchase'. currency is always 'XSGD'. "
            "max_amount is a number. If the amount is ambiguous, use 0."
        )

        messages = [
            {"role": "user", "content": user_message},
        ]

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-06-01",
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": messages,
                    }
                ),
            )

            response_body = json.loads(response["body"].read())
            raw = response_body["content"][0]["text"]
            data = json.loads(raw)

            return Intent(
                action=data.get("action", "purchase"),
                product=data.get("product", ""),
                merchant=data.get("merchant", ""),
                max_amount=float(data.get("max_amount", 0)),
                currency=data.get("currency", "XSGD"),
            )
        except Exception as e:
            # If Bedrock call fails, raise so caller can fall back
            raise RuntimeError(f"Bedrock intent parsing failed: {str(e)}")