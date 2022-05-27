import gspread
from google.oauth2.service_account import Credentials
from dataclasses import dataclass, field
from typing import List
import math


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
    item: str
    quantity: int
    price: float = 0.0

@dataclass
class Shop:
    balance: float = 0.0
    stock: List[ProductStock] = field(default_factory=list)

@dataclass
class ProductOrder:
    item: str
    quantity: int

@dataclass
class Customer:
    name: str
    cash: float = 0.0
    order: List[ProductOrder] = field(default_factory=list)


def read_shop():
    """
    Stock the shop using the current_stock spreadsheet
    """
    shop = Shop()
    create_shop_stock = SHEET.worksheet('current_stock').get_all_values()
    shop.balance = float(create_shop_stock[0][0])
    for row in create_shop_stock[1:]:
        product = ProductStock(row[0], int(row[1]), float(row[2]))
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
        customer_product = ProductOrder(row[0], int(row[1]))
        customer.order.append(customer_product)

    return customer

def current_shop_stock(s):
    """
    Displays list of items on sale and the quantity in stock
    """
    print("\n------------------")
    print(f"The current shop balance is €{s.balance}")
    print("Items available and quantity currently in stock")
    print("------------------")

    for row in s.stock:
        print(f'{row.item} : {row.quantity}')
    print("------------------")


def new_customer_order():
    """
    Write the customer name, cash balalance and customer order to 
    the customer_order spreadsheet.
    Customer can continue more items if required.
    Each new customer order will clear the previous customers order.
    """
    worksheet_to_update = SHEET.worksheet('customer_order')
    worksheet_to_update.clear()

    customer_name = input("Hello, please enter your name: ")
    customer_balance = input("Please enter your cash balance: €")

    worksheet_to_update.append_row([customer_name, float(customer_balance)])

    while True:
        item_order = input("Please select item from shop stock: ")
        item_quantity = int(input("Please enter the amount you want: "))
        worksheet_to_update.append_row([item_order, item_quantity])

        shopping_complete = input("Is there anything else 'Y'/'N'?\n")
        if shopping_complete == "Y":
            continue
        elif shopping_complete == "N":
            break
        else:
            last_chance = input("Please select 'Y' or 'N'\nIs there anything else we can get you?\n")
            if last_chance != "Y":
                print("We will take that as a no. Thanks you and goodbye.")
                break

def customer_order(c):
    """
    Displays list of items and the quantity the customer has ordered
    """
    print("\n------------------")
    print("Items and the quantity requried by the customer")
    print("------------------")

    for row in c.order:
        print(f'{row.item} : {row.quantity}')
    print("------------------\n")

def process_customer_order(c, s):
    """
    Process a new or existing customer order.
    If an order cannot be processed, tell the customer
    """
    starting_cash = c.cash
    item_quantity_cost = float(0.00)
    
    valid_order = False

    print("The customer can purchase the following:")
    for cust_item in c.order:
        for stock_item in s.stock:
            product_cost = 0
            if cust_item.item == stock_item.item:
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

def execute_order(c, product_cost, stock_item, cust_item):
    """
    Execute the customer order.
    Only process valid orders where the item
    is in stock in the shop.
    Orders can only be executed based on the
    quantities in stock.
    """
    if c.cash >= product_cost:
        c.cash -= product_cost
        stock_item.quantity -= cust_item.quantity
        item_quantity_cost = stock_item.price * cust_item.quantity
        print(f"{cust_item.item} * {cust_item.quantity} = €{round((item_quantity_cost), 2)}")
    elif (product_cost > c.cash) & (c.cash >= stock_item.price):
        cust_item.quantity = math.floor(c.cash / stock_item.price)
        c.cash -= cust_item.quantity * stock_item.price
        stock_item.quantity -= cust_item.quantity
        item_quantity_cost = stock_item.price * cust_item.quantity
        print(f"{cust_item.item} * {cust_item.quantity} = €{round((item_quantity_cost), 2)}")
    elif c.cash < stock_item.price:
        print(F"You cannot afford to buy: {cust_item.item}")


def open_shop():
    """
    Provide 3 options to the user:
    1) See stock inventory
    2) Input customer order
    3) Complete existing customer order
    """
    stock_shop = read_shop()

    while True:
        print("\n\t---CORNER STORE---")
        print("\nPlease choose number 1-3 to proceed")
        print("1) Shop consumables and prices")
        print("2) Create new Customer Order")
        print("3) Execute existing costomer order")
        option_sel = input("\nEnter: ")

        if option_sel == "1":
            current_shop_stock(stock_shop)
        elif option_sel == "2":
            new_customer_order()
            cust_order = read_customer('customer_order')
            customer_order(cust_order)
            process_customer_order(cust_order, stock_shop)
        elif option_sel == "3":
            online_order = read_customer('online_order')
            customer_order(online_order)
            process_customer_order(online_order, stock_shop)
        else:
            print("The shop does not provide this service")
            break

def main():
    open_shop()

main()