import json
import numpy as np
from dataclasses import dataclass, field



#### CARTOON ORDERS, SIMPLE BUNDLE SETUP

## definition bundle 1:  4w Starter Set (sku-200)
# fixed price for 4 paid items + 4 freebies:
# 4 x meal-powder, all paid (sku-001)
# 1 x shaker for free (sku-002)
# 1 x diet plan for free (sku-003)
# 1 x cookbook for free (sku-004)
# 1 x vitamins for free (sku-005)

bundle_1 = \
    {'sku-200': {  # parent bundle: StarterSet 1
        'type': 'static price combo',
        'components': {
            'sku-001': {'n': 4, 'variant_sku': None, 'pricing': True}, # 4 packs of diet-powder
            'sku-002': {'n': 1, 'variant_sku': None, 'pricing': False},  # free shaker
            'sku-003': {'n': 1, 'variant_sku': None, 'pricing': False},  # free diet plan
            'sku-004': {'n': 1, 'variant_sku': None, 'pricing': False},  # free cookbook
            'sku-005': {'n': 1, 'variant_sku': None, 'pricing': False},  # free vitamins
        }
    }}


class base_dataclass:

    def convert_to_dict(self):



# definitions:
# product: article that may or may not be available in different variants
# item: sellable unit (ie., variant of a product)
# stock keeping unit (sku): id assigned to product, sellable item or bundle.
# sku format: sku-[a]-[b] -> [a] being product/bundle identifier, [b] -> product variant identifier
#
# @dataclass
# class cart_1:
#     # items: 1 x bundle_1, no other items in shopping cart
#     order_id = 1
#     item_sku: list = field(default_factory=lambda: [
#         'sku-200-001',
#         'sku-001-001', 'sku-001-002', 'sku-001-003',
#         'sku-002-001', 'sku-003-001', 'sku-004-001', 'sku-005-001'
#     ])
#     items_sold: list = field(default_factory=lambda:
#                              [1,
#                               1, 1, 2,
#                               1, 1, 1, 1])  # item quantities
#     n_prod: int = len(items_sold)
#
#     order_line_item_id: str = field(default_factory=lambda: [f'oli-{i}' for i in range(1, n_prod + 1)])
#     order_line_id: int = field(default_factory=lambda: list(range(1, n_prod + 1)))
#     product_id: list =field(default_factory=lambda:
#                         ['mf-b-4wStarterSet'] +\
#                         ['mf-p-powder'] * 3 +\
#                         ['mf-p-shaker', 'mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'])
#     product_price: float = field(default_factory=lambda: [179.84] + [179.84 / 4] * 2 + [179.84 / 4 * 2] + [0.] * 4)
#     item_index: int = np.cumsum(items_sold).tolist(),
#     items_sold: int = items_sold,
#     item_sku: list = field(default_factory=lambda: item_sku)
#     bundle_id: str = field(default_factory=lambda: ['sku-200-StarterSet4w'] * n_prod)
#     bundle_property: str = [json.dumps(bundle_1)] * n_prod,
#     product_sku: list = field(default_factory=lambda: [x[:7] for x in item_sku])



## test order #1
# items: 1 x bundle_1, no other items in shopping cart
cart_id = 1
items_sold = [1, 1, 1, 2, 1, 1, 1, 1] # item quantities
n_prod =  len(items_sold) # product defined here as sellable unit that may or may not be available in different variants

cart_1 = {
    'order_line_item_id': [f'oli-{i}' for i in range(1,n_prod+1)],
    'order_line_id': list(range(1, n_prod+1)),
    'order_id': [f'#{cart_id}'] * n_prod,

    'product_id':
        ['mf-b-4wStarterSet'] +
        ['mf-p-powder'] * 3 +
        ['mf-p-shaker', 'mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'],
    'product_price': [179.84] + [179.84 / 4] * 2 + [179.84 / 4 * 2] + [0.] * 4,  # Price in purchase order

    'item_index': np.cumsum(items_sold).tolist(),
    'items_sold': items_sold,
    'item_sku': [ # format sku-[a]-[b] -> sku-[a] is the product_sku
        'sku-200-001',
        'sku-001-001', 'sku-001-002', 'sku-001-003',
        'sku-002-001', 'sku-003-001', 'sku-004-001', 'sku-005-001'
    ],

    'bundle_id': ['sku-200-StarterSet4w'] * n_prod,
    'bundle_property': [json.dumps(bundle_1)] * n_prod,
}

cart_1['product_sku'] =  [x[:7] for x in cart_1['item_sku']]


## test order #2
# items: 2 x bundle_1, missing one free shaker and has additional paid items: 1x powder, 1x shaker
cart_id = 2
items_sold = [x * 2 if i != 4 else x for i, x in enumerate([1, 1, 1, 2, 1, 1, 1, 1])] + [1, 3] # item quantities
n_lines =  len(items_sold) # defined here as: n unique variants

cart_2 = {
    'order_line_item_id': [f'oli-{i}' for i in range(1, n_lines+1)],
    'order_line_id': list(range(1, n_lines+1)),
    'order_id': [f'#{cart_id}'] * n_lines,

    'bundle_id': ['sku-200-StarterSet4w'] * n_lines,
    'bundle_property': [json.dumps(bundle_1)] * (n_lines -1) + [None],

    'product_id':
        ['mf-b-4wStarterSet'] +
        ['mf-p-powder'] * 3 +
        ['mf-p-shaker', 'mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'] +
        ['mf-p-powder', 'mf-p-shaker'],

    'item_index': np.cumsum(items_sold).tolist(),
    'item_sku': [ # format sku-[a]-[b] -> sku-[a] is the product_sku
        'sku-200-001',
        'sku-001-001', 'sku-001-002', 'sku-001-003',
        'sku-002-001', 'sku-003-001', 'sku-004-001', 'sku-005-001',
        'sku-001-001', 'sku-002-001',
    ],

    'items_sold': items_sold,
    'product_price': [179.84] + [179.84/4] * 2 + [179.84/4*2] + [0.] * 4 + [100., 9.],  # Price in purchase order
}

cart_2['product_sku'] =  [x[:7] for x in cart_2['item_sku']]


## test order 3
# items: 1 x bundle_1, missing free shaker from bundle and +1 free shaker from different promo (e.g. customer loyalty)
cart_id = 3
items_sold = [1, 1, 1, 2, 1, 1, 1, 1] # item quantity
n_lines =  len(items_sold) # product defined here as sellable unit that may or may not be available in different variants

cart_3 = {
    'order_line_item_id': [f'oli-{i}' for i in range(1,n_lines+1)],
    'order_line_id': list(range(1, n_lines+1)),
    'order_id': [f'#{cart_id}'] * n_lines,

    'product_id':
        ['mf-b-4wStarterSet'] +
        ['mf-p-powder'] * 3 +
        ['mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'] +
        ['mf-p-shaker'],


    'product_price': [179.84] + [179.84 / 4] * 2 + [179.84 / 4 * 2] + [0.] * 4,  # Price in purchase order

    'item_index': np.cumsum(items_sold).tolist(),
    'items_sold': items_sold,
    'item_sku': [ # format sku-[a]-[b] -> sku-[a] is the product_sku
        'sku-200-001',
        'sku-001-001', 'sku-001-002', 'sku-001-003',
        'sku-003-001', 'sku-004-001', 'sku-005-001',
        'sku-002-001'
    ],

    'bundle_id': ['sku-200-StarterSet4w'] * (n_lines - 1) + [None],
    'bundle_property': [json.dumps(bundle_1)] * (n_lines - 1) + [None],
}

cart_3['product_sku'] =  [x[:7] for x in cart_3['item_sku']]
