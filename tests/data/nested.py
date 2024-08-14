import json
import numpy as np

#### CARTOON PRODUCT BUNDLES AND SHOPPING CARTS (ORDERS)

# Define the bundles
starterSet4w = {
        'type': 'static price combo',
        'components': {
            'sku-001': {'n': 4, 'variant_sku': None, 'pricing': True}, # 4 packs of diet-powder
            'sku-002': {'n': 1, 'variant_sku': None, 'pricing': False},  # free shaker
            'sku-003': {'n': 1, 'variant_sku': None, 'pricing': False},  # free diet plan
            'sku-004': {'n': 1, 'variant_sku': None, 'pricing': False},  # free cookbook
            'sku-005': {'n': 1, 'variant_sku': None, 'pricing': False},  # free vitamins
        }
}

# buy one-get one (10% discount on specific flavour variant)
bogo10 = {
        'type': 'BOGO 10%',
        'components': {
            'sku-001': {'n': 1, 'variant_sku': None, 'pricing': True},
            'sku-002': {'n': 1, 'variant_sku': 'sku-001-099', 'pricing': 'd10'},  # 10% discount for new flavour variant
        }
}

# define combined bundle
nested_bundle = {
    'sku-300': {  # Parent bundle: StarterSet 4w + BOGO
        'type': 'nested bundle',
        'components': {
            # child bundles
            'sku-100': starterSet4w,
            'sku-200': bogo10
        }
    }
}

## Test order #4
# 1 x nested_bundle + 1 x additional item of the BOGO discounted flavour variant (not payed)
cart_id = 1
items_sold = [1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1] # item quantity
n_prod =  len(items_sold) # product defined here as sellable unit that may or may not be available in different variants

cart_4 = {
    'order_line_item_id': [f'oli-{i}' for i in range(1,n_prod+1)],
    'order_line_id': list(range(1, n_prod+1)),
    'order_id': [f'#{cart_id} (nested)'] * n_prod,

    'product_id':
        ['mf-b-4wStarterSet'] +
        ['mf-p-powder'] * 3 +
        ['mf-p-shaker', 'mf-p-dplan', 'mf-p-cookbook', 'mf-p-vitamins'] +
        ['mf-p-powder', 'mf-p-powder', 'mf-p-powder'],
    'product_price': [None] + [179.84 / 4] * 2 + [179.84 / 4 * 2] + [0.] * 4 + [179.84 / 4, 179.84 / 4 * 0.9, 179.84 / 4] ,  # Price in purchase order

    'item_index': np.cumsum(items_sold).tolist(),
    'items_sold': items_sold,
    'item_sku': [ # format sku-[a]-[b] -> sku-[a] is the product_sku
        'sku-400-001',
        'sku-001-001', 'sku-001-002', 'sku-001-003',
        'sku-002-001', 'sku-003-001', 'sku-004-001', 'sku-005-001',
        'sku-001-004', 'sku-001-099', 'sku-001-005'
    ],

    'bundle_id': ['sku-200-StarterSet4w'] * n_prod,
    'bundle_property': [json.dumps(nested_bundle)] * (n_prod-1) + [None],
}

cart_4['product_sku'] =  [x[:7] for x in cart_4['item_sku']]
cart_4['product_price'][0] = sum(cart_4['product_price'][1:])
