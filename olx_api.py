import threading
import time

import requests
from bs4 import BeautifulSoup


class OLXRequests:
    url = 'https://www.olx.pl/elektronika/komputery/komputery-stacjonarne/'

    def __init__(self, lock: threading.Lock, rpm: int = 60):
        self.lock = lock
        self.rps = (rpm - 1) / 60
        self._last_request_time = 0

    @staticmethod
    def _get_html(page: int):
        payload = {
            'search[order]: created_at': 'desc',
            'search[dist]': '30',
            'page': page,
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/84.0.4147.105 Safari/537.36 OPR/70.0.3728.106'}
        response = requests.get(OLXRequests.url, params=payload, headers=headers)
        if response.status_code != 200:
            return False
        return response.content

    @staticmethod
    def get(stop_page: int = 2, start_page: int = 1):
        def get_links():
            h = soup.find('div', 'content')
            h = h.find('div', 'rel listHandler')
            r = h.find('table', 'fixed offers breakword offers--top redesigned').tbody
            l = h.find('table', 'fixed offers breakword redesigned').tbody
            r.append(l)
            offer = r.find_all('div', 'offer-wrapper')
            for x in offer:
                links.append(x.table.tbody.tr.td.a['href'])

        links = []

        while 1:

            content = OLXRequests._get_html(start_page)
            if not content or start_page > stop_page:
                break
            soup = BeautifulSoup(content, 'html.parser')
            get_links()
            start_page += 1
        return links

    def get_description(self, url: str) -> [str, float]:
        def request_time_moderator():
            now = time.time()
            delta_t = (now - self._last_request_time) - (1 / self.rps)
            if delta_t < 0:
                time.sleep(abs(delta_t))

        with self.lock:
            request_time_moderator()
            response = requests.get(url)
            self._last_request_time = time.time()

        soup = BeautifulSoup(response.content, 'html.parser')
        price = soup.find('div', class_='pricelabel')
        try:
            price = float(str(price.strong.text.replace('zł', '').replace(' ', '').strip().lower()))
        except:
            price = float('inf')

        soup = soup.find('div', id='textContent')
        return [soup.text, price]
