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
    shop.balance = float(create_shop_stock[0][1])
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
        print(f'#{row.id} : {row.item.upper()} : {row.quantity}')
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
        id_check = input("\nSELECT ITEM FROM SHOP BY ENTERING ID#:\n")
        item_order = order_check(id_check, c)
        if item_order == False:
            break
        quant_check = input("ENTER THE QUANTITY YOU REQUIRE:\n")
        item_quantity = order_check(quant_check, c)
        if item_quantity == False:
            break
        worksheet_to_update.append_row([item_order, item_quantity])

        shopping_complete = input("ANYTHING ELSE 'Y'/'N'?\n").upper().strip()
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


def order_check(int_check, c):
    """
    Check to confirm id# and quantity are integer values
    If criteria not met then customer is notified
    and False returned
    """
    if int_check.isdigit():
        int_check = int(int_check) 
        return int_check
    else:
        print("\nTHIS ORDER IS NOT VALID")
        int_check = False
        return int_check


def customer_order(c):
    """
    Displays list of items and the quantity the customer has ordered
    """
    print("\n------------------")
    print("ITEM ID# AND QUANTITY REQUIRED BY THE CUSTOMER")
    print("------------------")

    for row in c.order:
        print(f'ID #{row.id} | QUANTITY:{row.quantity}')
    print("------------------\n")


def process_customer_order(c, s):
    """
    Process a new or existing customer order.
    """
    starting_cash = c.cash
    valid_order = False

    print("THE CUSTOMER CAN PURCHASE THE FOLLOWING:")
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
        print("\n------------------")
        print("SORRY WE DO NOT HAVE WHAT YOU WANT")

    s.balance += (starting_cash - c.cash)
    print("\n------------------")
    print(f"TOTAL COST FOR CUSTOMER IS €{round((starting_cash - c.cash), 2)}.")
    print(f"{c.name.upper()}, HAS €{round((c.cash), 2)} REMAINING.")
    print(f"THE SHOP BALANCE IS €{s.balance}.")
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
        print(f"ID #{c_item.id}: {stock_item.item.upper()} * {c_item.quantity} = €{round((items_cost), 2)}")
        update_shop(stock_item.item, c_item.quantity, items_cost)
    elif (product_cost > c.cash) & (c.cash >= stock_item.price):
        c_item.quantity = math.floor(c.cash / stock_item.price)
        c.cash -= c_item.quantity * stock_item.price
        stock_item.quantity -= c_item.quantity
        items_cost = stock_item.price * c_item.quantity
        print(f"ID #{c_item.id}: {stock_item.item.upper()} * {c_item.quantity} = €{round((items_cost), 2)}")
        update_shop(stock_item.item, c_item.quantity, items_cost)
    elif c.cash < stock_item.price:
        print(F"\nSORRY YOU CANNOT AFFORD:")
        print(F"ID #{c_item.id}: {stock_item.item.upper()}")

def update_shop(i, q, i_c):
    """
    Update the shop balance and the stock inventory 
    in the google spreadsheet current_stock for executed orders.
    This is so the database remains up to date.
    """
    ws_shop_update = SHEET.worksheet('current_stock')
    ws_shop = ws_shop_update.get_all_values()

    shop_recieve = i_c
    shop_balance = float(ws_shop[0][1]) + shop_recieve
    shop_balance = str(shop_balance)
    ws_shop_update.update_cell(1, 2, shop_balance)

    for row in ws_shop:
        if row[1] == i:
            update_quant = int(row[2]) - q
            update_quant = str(update_quant)
            row = int(row[0]) + 1
            col = 3
            ws_shop_update.update_cell(row, col, update_quant)


def open_shop():
    """
    Provide 3 options to the user:
    1) Display shop cash balance, current stock, prices & inventory
    2) Create and process the customer order
    3) Restock the shop at wholesale prices - cost is 70% of the 
        replaced items sale price
    """
    stock_shop = read_shop()

    while True:
        print("\n\t---CORNER STORE---")
        print("\nPLEASE CHOOSE OPTION 1-3 TO PROCEED")
        print("1) CURRENT SHOP STOCK, PRICES & INVENTORY")
        print("2) CREATE & PROCESS A NEW CUSTOMER ORDER")
        print("3) RESTOCK DEPLETED SHOP STOCK AT WHOLESALE DISCOUNT PRICES")
        option_sel = input("\n")

        if option_sel == "1":
            current_shop_stock(stock_shop)
        elif option_sel == "2":
            new_customer_order(stock_shop)
            cust_order = read_customer('customer_order')
            customer_order(cust_order)
            process_customer_order(cust_order, stock_shop)
        elif option_sel == "3":
            restock_shop = read_shop()
            for rs_q, s_q in zip(restock_shop.stock, stock_shop.stock):
                stock_required = rs_q.quantity - s_q.quantity
                shop_cost = (stock_required * (s_q.price * 0.7))
                s_q.quantity += stock_required
                stock_shop.balance -= shop_cost
            current_shop_stock(stock_shop)
        else:
            print("------------------")
            print("THE SHOP DOES NOT PROVIDE THIS SERVICE")
            print("------------------") 


def main():
    open_shop()


main()
