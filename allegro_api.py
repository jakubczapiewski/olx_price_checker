import base64
import json
import threading
import time

import requests


class AllegroRequests:
    requests_url = 'https://api.allegro.pl'
    auth_url = "https://allegro.pl/auth/oauth/token"

    def __init__(self, client_id: str, client_secret: str, lock: threading.Lock = threading.Lock(), rpm: int = 9000):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = ""
        self._expires_in = 0
        self._jti = ""
        self._token_type = ''
        self._session = requests.Session()
        # requests Lock
        self.lock = lock
        # maximum number of requests pre second
        self.rps = (rpm - 1) / 60
        self._last_request_time = 0

    def authorize(self) -> None:
        code = f"{self.client_id}:{self.client_secret}".encode('utf-8')
        aut_code = base64.b64encode(code).decode('utf-8')
        headers = {"Authorization": f"Basic {aut_code}"}
        payload = {"grant_type": "client_credentials"}
        try:
            response = requests.post(url=AllegroRequests.auth_url, headers=headers, params=payload).json()
        except:
            raise SystemError('Allegro Authorization problems.')
        try:
            self._access_token = response['access_token']
            self._expires_in = response['expires_in']
            self._jti = response['jti']
            self._token_type = response['token_type']
        except:
            raise SystemError('Allegro Authorization problems. Check your client id and secret key.')

    def request(self, method: str, url: str, payload: dict, accept: str) -> json:
        def request_time_moderator():
            now = time.time()
            delta_t = (now - self._last_request_time) - (1 / self.rps)
            if delta_t < 0:
                time.sleep(abs(delta_t))

        url = AllegroRequests.requests_url + url
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept-Language": "pl",
            "Accept": accept
        }

        req = requests.Request(method, url=url, headers=headers, params=payload).prepare()
        with self.lock:
            request_time_moderator()
            response = self._session.send(req).json()
            self._last_request_time = time.time()
        return response


class SearchEngine:
    _api_v1 = "application/vnd.allegro.public.v1+json"

    def __init__(self, allegro: AllegroRequests):
        self.allegro = allegro
        self.allegro.authorize()

    def search_offer(self, category_id: str = None, phrase: str = None, product_status='used') -> json:
        response = False
        try_count = 5
        url = "/offers/listing"
        sort = '+price'
        status = {
            "new": '11323_1',
            "used": '11323_2',
        }
        payload = {
            'category.id': category_id,
            'phrase': phrase,
            'sort': sort,
            "parameter.11323": status[product_status],
            "sellingMode.format": 'BUY_NOW'
        }
        for x in range(try_count):
            try:
                response = self.allegro.request(method='get', url=url, payload=payload, accept=SearchEngine._api_v1)
                break
            except:
                pass
        return response

    def search_category(self, parent_id: str = None) -> requests.Response:
        url = "/sale/categories"
        payload = {}
        if parent_id:
            payload['parent.id'] = parent_id
        response = self.allegro.request(method='get', url=url, payload=payload, accept=SearchEngine._api_v1)
        response = response['categories']

        return response
