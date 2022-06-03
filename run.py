"Import the required libraries"
from dataclasses import dataclass, field
from typing import List
import math
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('corner_store')


@dataclass
class ProductStock:
    id: int
    item: str
    quantity: int
    price: float = 0.0


@dataclass
class Shop:
    balance: float = 0.0
    stock: List[ProductStock] = field(default_factory=list)


@dataclass
class ProductOrder:
    id: int
    quantity: int


@dataclass
class Customer:
    name: str
    cash: float = 0.0
    order: List[ProductOrder] = field(default_factory=list)


def read_shop():
    """
    Stock the shop dataclass using the current_stock spreadsheet.
    """
    shop = Shop()
    create_shop_stock = SHEET.worksheet('current_stock').get_all_values()
    shop.balance = float(create_shop_stock[0][0])
    for row in create_shop_stock[1:]:
        product = ProductStock(int(row[0]), row[1], int(row[2]), float(row[3]))
        shop.stock.append(product)

    return shop


def read_customer(filepath):
    """
    Read the customer order from the customer_order spreadsheet
    """
    customer_order = SHEET.worksheet(filepath).get_all_values()
    customer_info = customer_order[0]
    customer = Customer(customer_info[0], float(customer_info[1]))

    for row in customer_order[1:]:
        customer_product = ProductOrder(int(row[0]), int(row[1]))
        customer.order.append(customer_product)

    return customer


def current_shop_stock(s):
    """
    Displays the shop balance and a list of items
    for sale and the quantity currently in stock
    """
    print("------------------")
    print("ID#: ITEM: IN STOCK")
    for row in s.stock:
        print(f'#{row.id} : {row.item} : {row.quantity}')
    print("\n------------------")
    print("SEE ABOVE: ID #, ITEM, QUANTITY IN STOCK")
    print(f"THE CURRENT SHOP BALANCE IS €{round(s.balance, 2)}")
    print("------------------")


def new_customer_order(c):
    """
    Write the customer name, cash balance and customer order to 
    the customer_order spreadsheet.
    Customer can continue adding as many items as required.
    Each new customer order will clear the previous one from the spreadsheet.
    """
    worksheet_to_update = SHEET.worksheet('customer_order')
    worksheet_to_update.clear()

    customer_name = input("Hello, please enter your name:\n")
    try:
        customer_balance = input("Please enter your cash balance in euros:\n")
        customer_details = [customer_name, float(customer_balance)]
    except ValueError:
        print("You have entered an invalid cash amount")
        open_shop()

    worksheet_to_update.append_row(customer_details)

    current_shop_stock(c)

    while True:
        item_order = int(input("ENTER ITEM #:\n"))
        item_quantity = int(input("ENTER AMOUNT REQUIRED:\n"))
        worksheet_to_update.append_row([item_order, item_quantity])

        shopping_complete = input("IS THERE ANYTHING ELSE 'Y'/'N'?\n").upper().strip()
        if shopping_complete == "Y":
            continue
        elif shopping_complete == "N":
            break
        else:
            print("\nINVALID OPTION")
            print("PLEASE SELECT Y/N")
            last_chance = input("\n")
            if last_chance != "Y":
                break


def customer_order(c):
    """
    Displays list of items and the quantity the customer has ordered
    """
    print("\n------------------")
    print("ITEMS AND QUANTITY REQUIRED BY THE CUSTOMER")
    print("------------------")

    for row in c.order:
        print(f'#{row.id} | quantity:{row.quantity}')
    print("------------------\n")


def process_customer_order(c, s):
    """
    Process a new or existing customer order.
    """
    starting_cash = c.cash
    valid_order = False

    print("The customer can purchase the following:")
    for cust_item in c.order:
        for stock_item in s.stock:
            product_cost = 0
            if cust_item.id == stock_item.id:
                valid_order = True
                if cust_item.quantity <= stock_item.quantity:
                    product_cost += cust_item.quantity * stock_item.price
                    execute_order(c, product_cost, stock_item, cust_item)
                elif cust_item.quantity > stock_item.quantity:
                    cust_item.quantity = stock_item.quantity
                    product_cost += cust_item.quantity * stock_item.price
                    execute_order(c, product_cost, stock_item, cust_item)

    if not valid_order:
        print("\nSorry we don't have anything you are looking for")
        print("Please look at the current available stock or shop online\n")

    s.balance += (starting_cash - c.cash)
    print("\n------------------")
    print(f"Total cost for customer is €{round((starting_cash - c.cash), 2)}.")
    print(f"{c.name}, has €{round((c.cash), 2)} remaining.")
    print(f"The shop balance is €{s.balance}.")
    print("------------------\n") 


def execute_order(c, product_cost, stock_item, c_item):
    """
    Execute the customer order.
    If an order cannot be executed, tell the customer.
    Reasons for not processing order include insufficient cash,
    insufficient stock or items not included in shop stock.
    """
    if c.cash >= product_cost:
        c.cash -= product_cost
        stock_item.quantity -= c_item.quantity
        items_cost = stock_item.price * c_item.quantity
        print(f"#{stock_item.item} * {c_item.quantity} = €{round((items_cost), 2)}")
    elif (product_cost > c.cash) & (c.cash >= stock_item.price):
        c_item.quantity = math.floor(c.cash / stock_item.price)
        c.cash -= c_item.quantity * stock_item.price
        stock_item.quantity -= c_item.quantity
        items_cost = stock_item.price * c_item.quantity
        print(f"{stock_item.item} * {c_item.quantity} = €{round((items_cost), 2)}")
    elif c.cash < stock_item.price:
        print(F"You cannot afford to buy: {stock_item.item}")


def open_shop():
    """
    Provide 3 options to the user:
    1) See stock inventory
    2) Input customer order
    3) Complete existing online customer order
    4) Restock the shop at a cost of 70% of the 
        replaced items sale price
    """
    stock_shop = read_shop()

    while True:
        print("\n\t---CORNER STORE---")
        print("\nPlease choose option 1-4 to proceed")
        print("1) Shop consumables and prices")
        print("2) Create new Customer Order")
        print("3) Execute existing online customer order")
        print("4) Restock the shop shelves at wholesale discount price")
        option_sel = input("\n")

        if option_sel == "1":
            current_shop_stock(stock_shop)
        elif option_sel == "2":
            new_customer_order(stock_shop)
            cust_order = read_customer('customer_order')
            customer_order(cust_order)
            process_customer_order(cust_order, stock_shop)
        elif option_sel == "3":
            online_order = read_customer('online_order')
            customer_order(online_order)
            process_customer_order(online_order, stock_shop)
        elif option_sel == "4":
            restock_shop = read_shop()
            for rs_q, s_q in zip(restock_shop.stock, stock_shop.stock):
                stock_required = rs_q.quantity - s_q.quantity
                shop_cost = (stock_required * (s_q.price * 0.7))
                s_q.quantity += stock_required
                stock_shop.balance -= shop_cost
            current_shop_stock(stock_shop)
        else:
            print("------------------")
            print("The shop does not provide this service")
            print("------------------") 
            open_shop()


def main():
    open_shop()


main()
