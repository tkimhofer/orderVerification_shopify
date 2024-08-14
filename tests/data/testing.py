from linear import order_1
from app.quality_assurance_toolbox import OrderCheckShopify
from collections import Counter
import unittest

class TestStringMethods(unittest.TestCase):

    def test_cart_1_result_exists(self):
        order = OrderCheckShopify(order_1)
        order.validate_basket_items()
        self.assertEqual(list(order.free_item_mismatch.keys()), ['excess', 'lack'])


    def test_cart_2_result(self):
        order = OrderCheckShopify()
        order.validate_basket_items()
        self.assertEqual(order.free_item_mismatch.values(), {'excess': Counter({'sku-002': 1}), 'lack': Counter()})

    def test_cart_3_result(self):
        order = OrderCheckShopify()
        order.validate_basket_items()
        self.assertEqual(order.free_item_mismatch.values(), {'excess': Counter({'sku-002': 1}), 'lack': Counter()})


if __name__ == '__main__':
    unittest.main()