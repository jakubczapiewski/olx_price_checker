import copy
import json
import os
import threading
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

from allegro_api import SearchEngine, AllegroRequests
from olx_api import OLXRequests
from price_calculator import PriceCalculator


def main(
        client_id: str,
        client_secret: str,
        request_per_minute_olx: int = 60,
        only_profitable: bool = True,
        offer_check_function=lambda x: True
) -> json:
    lock = threading.Lock()
    request = AllegroRequests(client_id, client_secret, lock)
    olx_requests = OLXRequests(lock, request_per_minute_olx)
    search_engine = SearchEngine(request)

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        desc = []
        for offer in olx_requests.get(stop_page=1):
            if offer_check_function(offer):
                desc.append(executor.submit(PriceCalculator.get_price, offer, olx_requests, search_engine))
    outcome = {}
    for x in as_completed(desc):
        res = x.result()
        if (not only_profitable) or PriceCalculator.price_filter(copy.copy(res)):
            outcome.update(res)
    return outcome
