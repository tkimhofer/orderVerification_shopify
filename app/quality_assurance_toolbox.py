from collections import Counter
import json
import pandas as pd

# self=OrderCheckShopify(order_1)
# self.validate_basket_items()
# self.free_item_mismatch
# self.log_message()

class OrderCheckShopify:
    """Class verifies the number of free items in shopify order based on table shopify_order_lines"""

    def __init__(self, order_lines: dict):
        """ Arg: order_lines (dict): shopify_order_lines data for single order id (e.g., payload of Shopify webhook)"""
        self.order_lines = pd.DataFrame(order_lines)
        self.order_id = self.order_lines["order_id"].iloc[0]
        self.free_item_mismatch = {'excess': Counter(), 'lack': Counter()} # init for pipeline/result output

    def _extract_bundle_items(self, bundle_prop: dict, item_count: Counter):
        """(Recursively) extract product and variant/item information from (nested) bundle_property.
            Args:
                bundle_prop (dict): bundle information (columns bundle_property in table shopify_order_lines)
                item_count (Counter): init item counter, filled and passed on in each interation
            Returns:
                item_count (Counter): number of product_skus/variant_skus in respective bundle

        """
        bundle_id = next(iter(bundle_prop))
        components = bundle_prop[bundle_id]['components']

        for sku, details in components.items():
            if 'type' in details:  # Indicates a child bundle
                item_count = self._extract_bundle_items({sku: details}, item_count)
            else:
                item_type = 'payed' if details['pricing'] else 'free'
                sku = sku if details['variant_sku'] is None else details['variant_sku']
                item_count[(bundle_id, sku, item_type)] += details['n']

        return item_count

    def _match_skus(self, row: pd.Series, values_to_check: set):
        """Match product or item SKU in `row` with sku information in bundle prop.

        Args:
            row (pd.Series): row in table shopify_order_lines
            values_to_check (set): product_sku or item_sku defining a bundle

        Identified skus collected in `itms_crt` (instance variable), which is processed in`validate_basket_items()`
        """
        item_type = 'free' if row['product_price'] == 0 else 'payed'

        if row['product_sku'] in values_to_check:
            self.itms_crt.update({(row['product_sku'], item_type): row['items_sold']})
            return True
        elif row['item_sku'] in values_to_check:
            self.itms_crt.update({(row['item_sku'], item_type): row['items_sold']})
            return True

        return False

    def validate_basket_items(self):
        """Collect sku und pricing info from bundles, compare with respective order lines.

        Workflow:
            1. If items are sold in bundle: Extract bundle composition from bundle_prop. (product/item sku and quantity)
            2. Multiply item quantities from step 1 with bundle order quantity
            2. Match product/item skus between bundle composition and order lines
            3. Compare order quantity (n) and pricing type (payed/free)
            4. Count skus where item quantity and pricing type mismatch
                i) items present in order but not in bundle prop (excess of free items in order),
                ii) items found in bundle prop but not in order (lack of free items in order)
            5. Filter mismatches for only free items

        Free item-mismatches are store in instance variable `free_item_mismatch`, which is processed in `log_message()`
        """

        for bundle_property, df_items in self.order_lines.groupby('bundle_property'):
            if bundle_property:
                bp_dict = json.loads(bundle_property)

                # Extract bundle items and their quantities
                extracted_itms = self._extract_bundle_items(bp_dict, Counter())

                # get bundle quantity in line order
                multiplier = df_items.set_index('product_sku')['items_sold'].to_dict()[next(iter(bp_dict))]

                # Multiply order quantity of bundle with item counts obtained from bundle_property (multiplier)
                itms_bdl = Counter({
                    (sku, payment): count * multiplier
                    for (bid, sku, payment), count in extracted_itms.items()
                })

                # Apply sku matching logic (bundle -> order lines)
                ids = set(map(lambda x: x[0], itms_bdl.keys()))
                self.itms_crt = Counter()
                df_items.apply(lambda row: self._match_skus(row, ids), axis=1)

                # compare bundle item quantities in shopping cart with the ones obtained from bundle_prop
                bdl_itms_not_crt = itms_bdl - self.itms_crt
                crt_itms_not_bdl = self.itms_crt - itms_bdl

                # filter for lacking/missing and excess free items
                self.free_item_mismatch['excess'] |= dict(filter(lambda x: x[0][1] == 'free', crt_itms_not_bdl.items()))
                self.free_item_mismatch['lack'] |= dict(filter(lambda x: x[0][1] == 'free', bdl_itms_not_crt.items()))


            else:
                # Free products not attached to bundle
                free_itms = df_items[df_items['product_price'] == 0]

                valid_free_itm = self._validate_free_nonbdl_items(free_itms) # dtype: list of bools
                if all(valid_free_itm):
                    continue

                free_itms_excess = free_itms.loc[map(lambda x: not x, valid_free_itm)]
                self.free_item_mismatch['excess'] |= Counter({(g, 'free'): data['items_sold'].sum()
                                                         for g, data in free_itms_excess.groupby('product_sku')})

    def log_message(self):
        '''Preparing message for stackeholders reporting
            Returns:
                tuple(bool, str): True as first element (bool) indicates that no errors were found (ie.,
                                    no message to be send), second element (str) is the message for stakeholder
                                    reporting / logging
        '''

        if self.free_item_mismatch['excess'] or self.free_item_mismatch['lack']:

            message = f'***Quality Issue in Order {self.order_id}***\n\n'

            skus = '-' if not self.free_item_mismatch['excess'] else "\n".join(
                f"{sku[0]} (n={n})" for sku, n in self.free_item_mismatch['excess'].items())
            message += "Unaccounted free item(s): " + skus + '\n\n'

            skus =  '-' if not self.free_item_mismatch['lack'] else "\n".join(
                f"{sku[0]} (n={n})" for sku, n in self.free_item_mismatch['lack'].items())
            message += "Missing free item(s): " + skus + '\n\n'

            message += f'Manual review of Order {self.order_id} advised \U0001F60A'
            return True, message

        else:
            # not messaging stakeholders
            # todo: log result (e.g. append order_id to text file)
            return False, f'No Issue Detected in Order {self.order_id}\n'

    @staticmethod
    def _validate_free_nonbdl_items(df: pd.DataFrame):
        # todo: identify free cart items not bundled (e.g., in loyalty reward scenarios)
        ''' Args:
                df (pd.DataFrame): order_lines row subset mapping to cart items not bundled and where product_price =0
            Returns:
                (list of bools): `True` if product_price = 0 is valid for resp. item, `False` else-wise
        '''
        return [True] * df.__len__()

