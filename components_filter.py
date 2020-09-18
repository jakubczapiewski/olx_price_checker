import logging
import re
from typing import List

components_tags = {
    'gpu': ['grafika', 'karta graficzna', 'gpu', 'nvidia', 'gtx', 'geforce', 'rtx'],
    'cpu': ['procesor', 'cpu', 'i5', 'i7', 'i9', 'i3'],
    'ram': ['ramu', 'ram', 'ddr4', 'ddr3', 'pamięci', 'pamici', 'pamięć'],
}
components_filters = {
    'gpu': {
        'excluded': [
            'pcie', 'pci',
            'gddr5x', 'gddr6x', 'gddr4', 'gddr5', 'gddr6', 'ddr4', 'ddr5', 'ddr6',
            'dedykowana',
            'gwarancji', 'wydajana', 'wydajno',
            'lata', 'rok',
            'nowa', 'pami',
            'sprzedaje', ' sprzedaję', "karta", 'grafiki', 'pamięci', 'pamieci',
            'grafika', 'karta graficzna', 'gpu', 'nvidia', 'geforce', 'graficzna', 'gratis', 'grafa', 'moliwo zmiany',
        ],
        "is_not": ['intel', 'zintegrowana'],
    },
    'cpu': {
        'excluded': [
            'dedykowana', 'intel',
            'gwarancji', 'core',
            'lata', 'rok',
            'nowa', 'pcie', 'pci',
            'sprzedaje', ' sprzedaj', "karta", 'grafiki', 'pamici', 'pamieci',
            'procesor', 'cpu', 'pami', 'moliwo zmiany',
        ],

        "is_not": [],
    },
    'ram': {
        'excluded': [
            'dedykowana', 'intel',
            'gwarancji', 'core',
            'lata', 'rok', 'dual channel',
            'nowa', 'pcie', 'pci',
            'sprzedaje', ' sprzedaj', "karta", 'grafiki', 'pamici', 'pamieci',
            'pamieci', 'pamici', 'pami', 'moliwo zmiany',

        ],
        "is_not": [],
    }
}


class ComponentsFilter:
    @staticmethod
    def get_components(des: str) -> dict:
        res = {
            'cpu': ComponentsFilter.get_cpu(des),
            'gpu': ComponentsFilter.get_gpu(des),
            'ram': ComponentsFilter.get_ram(des),

        }
        logging.debug(res)
        return res

    @staticmethod
    def remove_characters(text: str) -> str:
        text = re.sub(r'[^a-zA-Z0-9 ]+', '', text)
        text = re.sub(r'( ){2}', ' ', text)
        text = text.strip()
        return text

    @staticmethod
    def text_normalization(text: str, excluded: list, is_not: list) -> str or False:
        text = ComponentsFilter.remove_characters(text)
        for ex in excluded:
            text = re.sub(r'\b' + ex + r'\b', '', text).strip()

        pattern = re.compile(r'^[0-9][ .]')
        r = [x for x in re.finditer(pattern, text)]
        if r:
            text = text[r[0].span()[1]:].strip()
        for i in is_not:
            if i in text.split():
                return False
        if len(text) > 100:
            return False
        return text

    @staticmethod
    def pattern_search(pattern: re.Pattern, des: str, tag: str) -> List[str]:
        result = []
        res = re.finditer(pattern, des.lower())
        res = [x for x in res]
        if res:
            excluded = components_filters[tag]['excluded']
            is_not = components_filters[tag]['is_not']
            for r in res:
                text = r.group()
                text = ComponentsFilter.text_normalization(text, excluded, is_not)
                if text:
                    result.append(text)
        return result

    @staticmethod
    def get_gpu(des: str) -> List[str]:
        tag = 'gpu'
        device = ''
        for x in components_tags['gpu']:
            device += x + '|'
        pattern = re.compile(r'(.)*(' + device[:-1] + r')(\w|.)*')

        text = ComponentsFilter.pattern_search(pattern, des, tag)
        text = [ComponentsFilter.remove_characters(t) for t in text]

        return text

    @staticmethod
    def get_cpu(des: str) -> List[str]:
        tag = 'cpu'
        p = r'(a[468].(\d){3,4}[k]?)|(i[3579].(\d){3,4}[kf]?)|((ryzen|[ ]r)[ ]?[3579]?[ -]?(\d){3,4}[x]?)'
        pattern = re.compile(p)
        text = ComponentsFilter.pattern_search(pattern, des, tag)
        text = [ComponentsFilter.remove_characters(t) for t in text]
        return text

    @staticmethod
    def get_ram(des: str) -> List[str]:
        tag = 'ram'
        device = ''
        for x in components_tags['ram']:
            device += x + '|'
        pattern = re.compile(r'(.)*(' + device[:-1] + r')(\w|.)*')
        text = ComponentsFilter.pattern_search(pattern, des, tag)
        text = [ComponentsFilter.remove_characters(t) for t in text]
        return text
