import json
import logging
import urllib.parse

import numpy as np

from allegro_api import SearchEngine
from components_filter import ComponentsFilter
from olx_api import OLXRequests


class PriceCalculator:
    categories_ids = {
        'gpu': 260019,
        'cpu': 257222,
        'mb': 4228,
        'ram': 257226,
        'case': 259436,
        'psu': 259437,
        'ssd': 257335,
        'hdd': 4476,
    }
    links = {
        260019: 'podzespoly-komputerowe-karty-graficzne-260019',
        257222: 'podzespoly-komputerowe-procesory-257222',
        4228: 'podzespoly-komputerowe-plyty-glowne-4228',
        257226: 'podzespoly-komputerowe-pamiec-ram-257226',
        259436: 'podzespoly-komputerowe-obudowy-259436',
        259437: 'podzespoly-komputerowe-zasilacze-259437',
        257335: 'dyski-i-pamieci-przenosne-dyski-ssd-257335',
        4476: 'dyski-i-pamieci-przenosne-dyski-hdd-4476',
    }

    @staticmethod
    def _lowest_price(tab: list) -> int:
        if not tab:
            return 0
        np_arr = np.array(tab)
        std = np_arr.std()
        avr = np.average(np_arr)
        res = np.array([x for x in np_arr if abs(avr - x) <= 1.5 * std])[0]
        return int(round(res))

    @staticmethod
    def get_offer(offers: json, name: str) -> dict or False:
        lowest_price: float = 0
        count: int = 0
        link: str = ''
        try:
            category_id = int(offers['categories']['subcategories'][0]['id'])
            link = f'https://allegro.pl/kategoria/{PriceCalculator.links[category_id]}?' + urllib.parse.urlencode(
                {"string": name, 'stan': 'używane', "offerTypeBuyNow": 1, 'order': 'p'})

            count = offers['searchMeta']['availableCount']

            price_tab = [float(x['sellingMode']['price']['amount']) for x in offers['items']['regular']]
            price_tab += [float(x['sellingMode']['price']['amount']) for x in offers['items']['promoted']]

            lowest_price = PriceCalculator._lowest_price(price_tab)
        except:
            pass
        return {
            'price': float(lowest_price),
            'count': count,
            'link': link,
            'name': name
        }

    @staticmethod
    def get_price(url: str, olx_requests: OLXRequests, search_engine: SearchEngine) -> dict:
        try:
            des, price = olx_requests.get_description(url)
            components = ComponentsFilter.get_components(des)
            result = {url: {'components': {}, 'price': float(price), 'allegro price': 0}}
            for category, component in components.items():
                case = {category: {'price': 0}}
                for name in component:
                    all_offers = search_engine.search_offer(category_id=str(PriceCalculator.categories_ids[category]),
                                                            phrase=name)
                    offer = PriceCalculator.get_offer(all_offers, name)

                    all_offers_new = search_engine.search_offer(
                        category_id=str(PriceCalculator.categories_ids[category]),
                        phrase=name, product_status='new')

                    new_offer_new = PriceCalculator.get_offer(all_offers_new, name)

                    offer['price for new'] = new_offer_new['price']
                    offer['count for new'] = new_offer_new['count']

                    if offer['price'] >= case[category]['price']:
                        case[category] = offer
                result[url]['components'].update(case)
                result[url]['allegro price'] += float(case[category]['price'])

            return result
        except:
            logging.error('Problems with get_price method')

    @staticmethod
    def price_filter(offer: dict) -> True or False:
        offer = offer.popitem()[1]
        price = offer['price']
        allegro_price = offer['allegro price']

        if price > 1000:
            # ram
            if offer['components']['ram']['price'] < 150:
                allegro_price -= offer['components']['ram']['price']
                allegro_price += 150
            # psu
            allegro_price += 150

            # case
            allegro_price += 150

            # mb
            allegro_price += 200

            if price > 1500:
                # hdd
                allegro_price += 100
                # ssd
                allegro_price += 150
        if price < (allegro_price * 1.1):
            return True
        return False
