import sqlite3

# define db scheme and dummy data
with sqlite3.connect(':memory:') as con:
  # #create a table
  # con.execute('''CREATE TABLE shopify_orders(
  #                   order_number INTEGER, # A unique numeric identifier for the order, used by both the shop owner and customer.
  #                   number xxx???
  #
  #                   subtotal_price FLOAT, #The price of the order before duties, shipping, and taxes.
  #                   total_tax NUMERIC, #The total cost of taxes.
  #                   has_taxes_included BOOLEAN,
  #                   note STRING,
  #                   cancelled_at TIMESTAMP,
  #                   created_on DATE,
  #                   adjusted_total_tax FLOAT,
  #                   total_items_ordered INTEGER,
  #                   total_products_ordered INTEGER,
  #                   total_items_refunded INTEGER,
  #                   total_customer_orders INTEGER,
  #                   utm_medium STRING,
  #                   campaign_id STRING,
  #                   customer_id STRING,
  #                   order_adjusted_amount FLOAT,
  #                   adjusted_total_price FLOAT
  #                   )''')

  con.execute(
    '''CREATE TABLE shopify_order_lines (
            order_id STRING NULLABLE, # unique id for every purchase
            
            order_line_item_id STRING NULLABLE,
            order_line_id INTEGER NULLABLE,
           
            product_id STRING NULLABLE, # product is 
            product_index INTEGER NULLABLE,
            ranked_product INTEGER NULLABLE,
            
            variant_id INTEGER NULLABLE, # product variant, e.g. flavour variant in shake
            item_index INTEGER NULLABLE,
            
            
            bundle_id STRING NULLABLE, # bundle... variant bundle or pack bundle... typically not assoc with free items
            
            products_sold INTEGER NULLABLE,
            product_price FLOAT NULLABLE,
            
            items_sold INTEGER NULLABLE,
            item_price FLOAT NULLABLE,
            
            fulfillable_quantity INTEGER NULLABLE, # sum of all line item quantities for fulfillment
            fulfillment_service STRING NULLABLE, # tracking order link
            fulfillment_status STRING NULLABLE, # success, open, pending, error, cancelled, failure
            
            requires_shipping BOOLEAN NULLABLE,
            vendor STRING NULLABLE,
            
            bundle_id STRING NULLABLE,
            bundle_type STRING NULLABLE,
            bundle_property STRING NULLABLE,
            
            
            
            products_refunded FLOAT NULLABLE,
            quantity_refunded FLOAT NULLABLE,
            subtotal_refunded FLOAT NULLABLE,
            
            product_sku STRING NULLABLE,
            sku_raw STRING NULLABLE,
            
           
            
            discount_amount FLOAT NULLABLE,
            pick_cost FLOAT NULLABLE,
            inbound_shipping_cost FLOAT NULLABLE,
            storage_cost FLOAT NULLABLE)'''

  )

  out = con.execute('select name from sqlite_master where type="table"').fetchall()
  print(out)



# problem
# gratis artikel fehlen (Versandkosten)
# zu viele gratisartikel

# gratis artikel: product_price = 0.0 (gratis artikel und auch andere artikel)
# starter_set mehrfach gekauft (mehr als einen bestimmten gratis artikel)



#### showing following concepts
# appropriate use of SQL
# OOP incl. class inheritance
# use of decorators
# functions as first class citizen
# typehints

# maybe also add:
#   advanced data structures
#   messaging and authentication
#   looting
#   automated documentation
#   visualisation of statitics?
#   use of parameter files for process automation?
#   MUST BE SIMPLE SETUP FOR IMPOROVED READABILITY TO PERFORM RELIABLE AND COMPLEX TASK!


### fullfillment status: order has been shipped (ie completed) partially/fully: yes/no

# object relation mapper
from sqlalchemy.orm import DeclarativeBase #choosing sqlalchemy for ORM (syntax closer to SQL)
from sqlalchemy.orm import registry, Mapped
import django.db as ddb # choosing django for messaging
mapper_registry = registry()

import datetime as dt

@mapper_registry.mapped
class Orders:
  order_number: int

  subtotal_price: float
  total_tax: float
  has_taxes_included: bool
  order_adjusted_amount: float
  adjusted_total_price: float

  total_products_ordered: int # skus
  total_items_ordered: int # incl different variants

  total_items_refunded: int

  total_customer_orders: int
  customer_id: str
  campaign_id: str

  note: str

  cancelled_at: dt.timestamp
  created_on: dt.timestamp



class Basket_items:
  order_id: Mapped[str, None]
  product_id: Mapped[str, None]
  fulfillable_quantity: Mapped[int, None] # not used -> out of stock

  order_line_item_id: Mapped[str, None]
  order_line_id: Mapped[int, None]

  fulfillable_quantity: Mapped[int, None]
  fulfillment_service: Mapped[str, None]
  fulfillment_status: Mapped[str, None]
  product_index: Mapped[int, None]
  item_index: Mapped[int, None]
  item_price: Mapped[float, None]
  items_sold: Mapped[int, None]
  requires_shipping: Mapped[bool, None]
  discount_amount: Mapped[float, None]
  variant_id: Mapped[int, None]
  vendor: Mapped[str, None]
  bundle_id: Mapped[str, None]
  bundle_type: Mapped[str, None]
  products_sold: Mapped[int, None]
  product_price: Mapped[float, None]
  quantity_refunded: Mapped[float, None]
  subtotal_refunded: Mapped[float, None]
  product_sku: Mapped[str, None]
  sku_raw: Mapped[str, None]
  bundle_property: Mapped[str, None]
  products_refunded: Mapped[float, None]
  ranked_product: Mapped[int, None]

  pick_cost: Mapped[float, None]
  inbound_shipping_cost: Mapped[float, None]
  storage_cost: Mapped[float, None]

class ConsistencyCheck(Orders, Basket_items):

  def __init__(self, dt_start:dt.datetime, dt_end:dt.datetime, offers_skus:dict):
    self.dt_start = dt_start
    self.dt_end = dt_end
    annot = {}

    self.establish_dbCon()
    self.collect_baskets()
    self.loop_baskets()
    self.send_message() # execute manually after review to prevent spamming receivers

  def establish_dbCon(self):

    pass

  def item_check(self, basket):
    pass

  def collect_baskets(self):
    pass

  def loop_baskets(self):

    for basket in range(100):
      result = self.item_check(basket)
      self.annot.update(result)

  def send_message(self):
    # parameterise messaging details and details
    # send message to recipients
    pass






# case definitions of free item logic
cases = {
  'sku 1': # free items
    {'Shaker': lambda x: sum([d==0 for d in x['price']]) == x['products_sold'][0],
     'Stoffwechselvitamine': lambda x: 0,
     'Rezeptbuch': lambda x: 0,
     'Ernährungsplan': lambda x: 0,
     'Shaker': lambda x: 0},
  'offer 1': {

  }
  # 'offer 1': { # price reduction
  #     'sku x': lambda x: x*0.5 # ex: 50% off of SKU 1 if product set 2 is purchased
  # }
}

def check_hist_orders(dt_start, dt_end):
  '''Consistency check for historical orders
    Args:
      dt_start (datetime): start datetime
      dt_end (datetime): end datetime
  '''
  pass

def update_orders():
  '''Check for updated/incoming orders post last run'''
  pass




