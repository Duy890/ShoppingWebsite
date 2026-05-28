import hashlib
import hmac
import uuid

import requests as http_requests

from ..core.config import get_settings


def create_momo_payment(amount: int, order_id: str, order_info: str) -> dict:
    s = get_settings()
    partner_code = s.MOMO_PARTNER_CODE
    access_key = s.MOMO_ACCESS_KEY
    secret_key = s.MOMO_SECRET_KEY
    redirect_url = s.MOMO_REDIRECT_URL
    ipn_url = s.MOMO_IPN_URL
    request_id = f"{order_id}_{uuid.uuid4().hex[:8]}"
    extra_data = ""
    request_type = "captureWallet"

    raw_signature = (
        f"accessKey={access_key}"
        f"&amount={amount}"
        f"&extraData={extra_data}"
        f"&ipnUrl={ipn_url}"
        f"&orderId={order_id}"
        f"&orderInfo={order_info}"
        f"&partnerCode={partner_code}"
        f"&redirectUrl={redirect_url}"
        f"&requestId={request_id}"
        f"&requestType={request_type}"
    )

    signature = hmac.new(
        secret_key.encode("utf-8"),
        raw_signature.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    payload = {
        "partnerCode": partner_code,
        "requestType": request_type,
        "ipnUrl": ipn_url,
        "redirectUrl": redirect_url,
        "orderId": order_id,
        "amount": amount,
        "orderInfo": order_info,
        "requestId": request_id,
        "extraData": extra_data,
        "lang": "vi",
        "signature": signature,
    }

    try:
        response = http_requests.post(
            s.MOMO_ENDPOINT,
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )
    except http_requests.exceptions.ConnectionError as e:
        raise ValueError(f"Cannot connect to MoMo gateway: {e}")
    except http_requests.exceptions.Timeout:
        raise ValueError("MoMo gateway timed out (>30s). Try again.")

    try:
        data = response.json()
    except Exception:
        raise ValueError(
            f"MoMo returned non-JSON response (HTTP {response.status_code}): {response.text[:200]}"
        )

    if data.get("resultCode", -1) != 0:
        raise ValueError(
            f"MoMo error {data.get('resultCode')}: {data.get('message', 'Unknown error')}"
        )

    return data


def verify_momo_ipn_signature(payload: dict) -> bool:
    s = get_settings()
    access_key = s.MOMO_ACCESS_KEY
    secret_key = s.MOMO_SECRET_KEY

    raw = (
        f"accessKey={access_key}"
        f"&amount={payload['amount']}"
        f"&extraData={payload['extraData']}"
        f"&message={payload['message']}"
        f"&orderId={payload['orderId']}"
        f"&orderInfo={payload['orderInfo']}"
        f"&orderType={payload['orderType']}"
        f"&partnerCode={payload['partnerCode']}"
        f"&payType={payload['payType']}"
        f"&requestId={payload['requestId']}"
        f"&responseTime={payload['responseTime']}"
        f"&resultCode={payload['resultCode']}"
        f"&transId={payload['transId']}"
    )

    expected = hmac.new(
        secret_key.encode("utf-8"),
        raw.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, payload.get("signature", ""))
