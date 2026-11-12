import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 15
DEFAULT_BASE_URL = 'https://www.wasenderapi.com/api'


def _safe_json_response(response: requests.Response) -> Dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        logger.warning('Wasender API returned a non-JSON response: %s', response.text)
        return {
            'success': False,
            'message': 'Invalid JSON response from WhatsApp service.',
            'status_code': response.status_code,
        }


def _request(
    method: str,
    url: str,
    api_key: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    content_type: bool = True,
) -> Dict[str, Any]:
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json',
    }
    if content_type:
        headers['Content-Type'] = 'application/json'

    try:
        print('REQUEST METHOD:', method)
        print('REQUEST URL:', url)
        print('REQUEST HEADERS:', headers)
        print('REQUEST PARAMS:', params)
        print('REQUEST BODY:', json)
        response = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json,
            timeout=DEFAULT_TIMEOUT,
        )
        print('RAW STATUS CODE:', response.status_code)
        print('RAW RESPONSE TEXT:', response.text)
        payload = _safe_json_response(response)
        print('WHATSAPP RESPONSE:', payload)
        if response.ok:
            return payload

        logger.warning('Wasender API request failed (%s): %s', response.status_code, payload)
        payload.setdefault('success', False)
        payload.setdefault('status_code', response.status_code)
        return payload
    except requests.RequestException as exc:
        print('WHATSAPP REQUEST EXCEPTION:', str(exc))
        logger.exception('Wasender API request error: %s', exc)
        return {
            'success': False,
            'message': str(exc),
        }

    except Exception as exc:
        print('WHATSAPP CRASH:', str(exc))
        import traceback
        traceback.print_exc()
        logger.exception('Unexpected Wasender API request error: %s', exc)
        return {
            'success': False,
            'message': str(exc),
        }
        

def is_on_whatsapp(phone: str, api_key: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/on-whatsapp/{phone}"
    return _request('GET', url, api_key, content_type=False)


def send_message(phone: str, text: str, api_key: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/send-message"
    return _request('POST', url, api_key, json={'to': phone, 'text': text})


def update_message(msg_id: str, text: str, api_key: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/messages/{msg_id}"
    return _request('PUT', url, api_key, json={'text': text})


def delete_message(msg_id: str, api_key: str, base_url: str = DEFAULT_BASE_URL) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}/messages/{msg_id}"
    return _request('DELETE', url, api_key, content_type=False)
