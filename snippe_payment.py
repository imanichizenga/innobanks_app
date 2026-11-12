# snippe_payment.py
import os
import uuid
from typing import Any, Dict, Optional

import requests


class SnippePaymentClient:
    """
    Snippe Payments API Client
    - Supports: Dynamic QR payments + mobile push payments
    - Uses env var: SNIPPE_API_KEY
    """

    BASE_URL = "https://api.snippe.sh/v1/payments"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        self.api_key = "snp_eafc95994870d887f0f02ed0ebea38b811e2a9ad40e0cc2cb0b447a20a5e1783"
        self.timeout = timeout

    def _headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())

        headers = {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotency_key,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
        except ValueError:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": "Invalid JSON response",
                "raw": response.text,
            }

        if response.status_code in (200, 201):
            return {"success": True, "data": data}

        return {"success": False, "status_code": response.status_code, "data": data}

    # ---------------------------
    # Dynamic QR Payment (Snippe requires details.amount + customer.email)
    # ---------------------------
    def create_dynamic_qr_payment(
        self,
        amount: int,
        phone_number: str,
        first_name: str,
        last_name: str,
        email: str,
        order_id: str,
        redirect_url: str = "",
        cancel_url: str = "",
        currency: str = "TZS",
        webhook_url: str = "",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "payment_type": "dynamic-qr",  # must be one of: mobile, card, dynamic-qr
            "details": {
                "amount": amount,          # REQUIRED by Snippe
                "currency": currency,
            },
            "phone_number": phone_number,
            "customer": {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,            # REQUIRED by Snippe
            },
            "webhook_url": webhook_url,
            "metadata": {"order_id": order_id},
        }

        # Only include redirect/cancel if you actually use them
        if redirect_url:
            payload["details"]["redirect_url"] = redirect_url
        if cancel_url:
            payload["details"]["cancel_url"] = cancel_url

        try:
            response = requests.post(
                url=self.BASE_URL,
                headers=self._headers(idempotency_key=idempotency_key),
                json=payload,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # ---------------------------
    # Mobile Push Payment (also uses details.amount)
    # ---------------------------
    def create_mobile_payment(
        self,
        amount: int,
        phone_number: str,
        first_name: str,
        last_name: str,
        email: str,
        order_id: str,
        currency: str = "TZS",
        webhook_url: str = "",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {
            "payment_type": "mobile",
            "details": {
                "amount": amount,          # REQUIRED pattern
                "currency": currency,
            },
            "phone_number": phone_number,
            "customer": {
                "firstname": first_name,
                "lastname": last_name,
                "email": email,            # likely required too (consistent)
            },
            "webhook_url": webhook_url,
            "metadata": {"order_id": order_id},
        }

        try:
            response = requests.post(
                url=self.BASE_URL,
                headers=self._headers(idempotency_key=idempotency_key),
                json=payload,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def list_payments(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Fetch recent payments from Snippe gateway."""
        params = {
            "limit": limit,
            "offset": offset,
        }
        try:
            response = requests.get(
                url=self.BASE_URL,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
