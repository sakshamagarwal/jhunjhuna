import logging
from kiteconnect import KiteConnect

GOLD_RATE = 4939

def login():    
    logging.basicConfig(level=logging.DEBUG)

    kite = KiteConnect(api_key="your_api_key")
    print(kite.login_url())
    request_token = input("Enter Request token: ")
    data = kite.generate_session("request_token_here", api_secret="your_secret")
    kite.set_access_token(data["access_token"])
    return kite

def get_bonds_list():
    # Returns list of bonds with details and max price
    return [
        {
            "name": "SGBJAN29",
            "exchange": "BSE",
            "max_price": GOLD_RATE,
            "isin": "IN0020200377"
        },
        {
            "name": "995EFL24",
            "exchange": "NSE",
            "max_price": 965,
            "isin": "INE804I077Z7"
        }
    ]

def place_buy_order(client, bond, exchange, price):
    try:
        order_id = client.place_order(
            tradingsymbol=bond,
            exchange=exchange,
            transaction_type=client.TRANSACTION_TYPE_BUY,
            quantity=1,
            order_type=client.ORDER_TYPE_LIMIT,
            price=price
        )
        return order_id
    except Exception as e:
        logging.info("Order placement failed: {}".format(e.message))

def update_buy_order(client, order_id, price):
    client.modify_order(
        variety = "regular",
        order_id = order_id,
        price = price
    )

def place_or_update_buy_order(client, bond, exchange, price):
    orders = client.orders()
    for order in orders:
        if order["tradingsymbol"] == bond:
            if order["price"] < price:
                update_buy_order(client, order["order_id"], price)
            return None
    place_buy_order(client, bond, exchange, price)

def is_holding_bond(client, bond):
    positions = client.positions()
    for item in positions:
        if item.tradingsymbol == bond:
            return True
    holdings = client.holdings()
    for item in holdings:
        if item.tradingsymbol == bond:
            return True
    return False

def get_highest_buyer(client, bond):
    quote = client.quote([bond])
    md = quote["depth"]["buy"]
    buy_prices = [depth_item[price] for depth_item in md]
    return max(buy_prices)

kite = login()
bonds_list = get_bonds_list()
for bond in bonds_list:
    if is_holding_bond(kite, bond["name"]):
        continue
    if get_highest_buyer(kite, bond["name"]) < bond["max_price"]:
        place_or_update_buy_order(kite, bond["name"], bond["exchange"], bond["price"])
    