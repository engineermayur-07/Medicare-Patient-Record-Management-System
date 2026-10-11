import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GeminiError(Exception):
    """Raised when Gemini cannot generate a response."""


def generate_response(api_key: str, model: str, system_prompt: str,
                      user_message: str) -> str:
    if not api_key:
        raise GeminiError('Gemini API key is not configured.')

    url = (
        f'https://generativelanguage.googleapis.com/v1beta/models/'
        f'{model}:generateContent?key={api_key}'
    )
    payload = {
        'systemInstruction': {
            'parts': [{'text': system_prompt}],
        },
        'contents': [{
            'role': 'user',
            'parts': [{'text': user_message}],
        }],
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 800,
        },
    }
    request = Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
    except HTTPError as exc:
        try:
            error_body = json.loads(exc.read().decode('utf-8'))
            error_message = error_body.get('error', {}).get('message')
        except (json.JSONDecodeError, UnicodeDecodeError):
            error_message = None
        detail = f' {error_message}' if error_message else ''
        raise GeminiError(
            f'Gemini request failed with HTTP {exc.code}.{detail}'
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GeminiError('Gemini is temporarily unavailable.') from exc

    try:
        return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise GeminiError('Gemini returned an empty response.') from exc
