import unittest

from components_filter import ComponentsFilter


class TestsComponentsFilter(unittest.TestCase):
    des = '''Specyfikacja:
    AMD Ryzen 5 3600 AM4
    MSI B450 GAMING PLUS MAX AM4
    MSI GeForce RTX 2060 SUPER GAMING X 8GB GDDR6 PCI-e
    2x Kingston 8GB DDR4 HyperX FURY Black Series KHX2400C12D4/8GX CL15
    Samsung SM951 256GB M.2 (MZ-VPV256HDGL-00000)
    EVGA SuperNOVA GS 650 80 Plus Gold (220-GS-0650-V2)
    i7-9800k
    BenQ XL2420G 24" LED/TN 1ms/G-Sync/Pivot
    HyperX Alloy FPS RGB Kailh Silver Speed (HX-KB1SS2-US)
    HyperX Pulsefire FPS Pro (HX-MC003B)
    MSI MAG Vapmiric 010 szkło
    Logitech LS21
    Windows 10 ENG/PL Home, uaktualniony do wersji Pro (pudełko z nośnikiem USB)
    '''

    def test_get_gpu(self):
        result = ['MSI RTX 2060 SUPER GAMING X 8GB'.lower()]
        self.assertEqual(ComponentsFilter.get_gpu(self.des), result)

    def test_get_cpu(self):
        result = [
            'ryzen 5 3600'.lower(),
            'i79800k'.lower()
        ]
        self.assertEqual(ComponentsFilter.get_cpu(self.des), result)

    def test_get_ram(self):
        result = ['2x kingston 8gb ddr4 hyperx fury black series khx2400c12d48gx cl15'.lower()]
        self.assertEqual(ComponentsFilter.get_ram(self.des), result)


if __name__ == '__main__':
    unittest.main()
