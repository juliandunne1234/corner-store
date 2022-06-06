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
    credit: float = 0.0
    order: List[ProductOrder] = field(default_factory=list)


@dataclass
class RestockOrder:
    id: int
    name: str
    quantity: int


@dataclass
class Restock:
    order: List[RestockOrder] = field(default_factory=list)


def read_shop():
    """
    Stock the shop dataclass using the current_stock
    google spreadsheet.
    The first row in the spreadsheet is the current
    shop balance in €'s.
    The next rows contain the product ID#, item name, price and quantity
    """
    shop = Shop()
    balance = SHEET.worksheet('shop_balance').get_all_values()
    shop.balance = float(balance[0][1])

    create_shop_stock = SHEET.worksheet('current_stock').get_all_values()
    for row in create_shop_stock[1:]:
        product = ProductStock(int(row[0]), row[1], int(row[2]), float(row[3]))
        shop.stock.append(product)

    return shop


def read_customer(filepath):
    """
    Read the customer order from the customer_order
    google spreadsheet.
    The first row in the spreadsheet includes the
    customer name and their shop credit in €'s.
    The next rows contain the product ID# and quantity
    they require of that product.
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
    Displays the current shop balance and lists the items
    for sale in the shop and the quantity currently in stock.
    """
    print("------------------")
    print("ID#: ITEM: IN STOCK")
    for row in s.stock:
        print(f'#{row.id} : {row.item.upper()} : {row.quantity}')
    print("\n------------------")
    print("SEE ABOVE: ID #, ITEM, QUANTITY IN STOCK")


def new_customer_order(c):
    """
    Write the customer name, account credit and customer order to
    the customer_order google spreadsheet.
    The customer can continue adding as many items as required.
    Each new customer order will clear the previous one from the spreadsheet.
    """
    worksheet_to_update = SHEET.worksheet('customer_order')
    worksheet_to_update.clear()

    # Customer can enter any name
    c_name = input("HELLO, PLEASE ENTER YOUR LOGIN NAME:\n")
    print(f"\nHELLO {c_name.upper()}, YOUR CORNER-STORE BALANCE IS €0.00")
    print(f"PLEASE ENTER THE AMOUNT IN EURO YOU WANT TO TOP UP BY")
    # If the customer enters an invalid number return to shop menu
    try:
        c_balance = float(input("\n"))
    except ValueError:
        print("TRANSACTION DECLINED - PLEASE TOP UP IN €'S ONLY")
        open_shop()

    # Update worksheet with customer name and account credit
    customer_details = [c_name, c_balance]
    worksheet_to_update.append_row(customer_details)

    current_shop_stock(c)
    print(f"{c_name.upper()} HAS €{round(c_balance, 2)} CREDIT TO SPEND")
    print("------------------")

    """
    Customer can order multiple items by selecting Y.
    Loop breaks when customer selects N or enters invalid data.
    """
    while True:
        id_check = input("\nSELECT ITEM FROM SHOP BY ENTERING ID#:\n")
        item_order = order_check(id_check, c)
        if item_order is False:
            break
        quant_check = input("ENTER THE QUANTITY YOU REQUIRE:\n")
        item_quantity = order_check(quant_check, c)
        if item_quantity is False:
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
            last_chance = input("\n").upper().strip()
            if last_chance != "Y":
                break


def order_check(int_check, c):
    """
    Check to confirm the product ID# and quantity entered
    are integer values. If this criteria is not met then the
    order is determined to be invalid.
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
    Displays list of items and the quantity the customer has ordered.
    """
    print("\n------------------")
    print("ITEM ID# AND QUANTITY REQUIRED BY THE CUSTOMER")
    print("------------------")

    for row in c.order:
        print(f'ID #{row.id} | QUANTITY:{row.quantity}')
    print("------------------\n")


def process_customer_order(c, s):
    """
    Process the customers order.
    Code checks that the product ID# entered is available in store.
    If True then the quantity required and the quantity in stock
    are checked and the customer can then purchase the amount
    required within their allowable account credit limit.
    """
    start_cred = c.credit
    valid_order = False

    print("THE CUSTOMER PURCHASED THE FOLLOWING:")
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

    s.balance += (start_cred - c.credit)
    print("\n------------------")
    print(f"TOTAL COST FOR CUSTOMER IS €{round((start_cred - c.credit), 2)}.")
    print(f"{c.name.upper()}, HAS €{round((c.credit), 2)} REMAINING.")
    print(f"THE SHOP BALANCE IS €{s.balance}.")
    print("------------------\n")


def execute_order(c, p_cost, s_item, c_item):
    """
    Execute the customer order.
    If an order cannot be executed, tell the customer.
    Reasons for not processing order include insufficient credit,
    insufficient stock or items not included in shop stock.
    """
    if c.credit >= p_cost:
        c.credit -= p_cost
        s_item.quantity -= c_item.quantity
        items = round((s_item.price * c_item.quantity), 2)
        print(f"#{c_item.id}|{s_item.item.upper()}*{c_item.quantity}=€{items}")
        update_shop(s_item.item, c_item.quantity, items)
    elif (p_cost > c.credit) & (c.credit >= s_item.price):
        c_item.quantity = math.floor(c.credit / s_item.price)
        c.credit -= c_item.quantity * s_item.price
        s_item.quantity -= c_item.quantity
        items = round((s_item.price * c_item.quantity), 2)
        print(f"#{c_item.id}|{s_item.item.upper()}*{c_item.quantity}=€{items}")
        update_shop(s_item.item, c_item.quantity, items)
    elif c.credit < s_item.price:
        print(F"\nSORRY YOU CANNOT AFFORD:")
        print(F"ID #{c_item.id}: {s_item.item.upper()}")


def update_shop(i, q, i_c):
    """
    Update the shop balance and the stock inventory
    in the current_stock google spreadsheet for executed orders.
    This is so the database remains up to date.
    """
    ws_shop_update = SHEET.worksheet('current_stock')
    ws_shop = ws_shop_update.get_all_values()
    ws_balance_update = SHEET.worksheet('shop_balance')
    ws_balance = ws_balance_update.get_all_values()

    shop_recieve = i_c
    shop_balance = float(ws_balance[0][1]) + shop_recieve
    shop_balance = str(shop_balance)
    ws_balance_update.update_cell(1, 2, shop_balance)

    for row in ws_shop:
        if row[1] == i:
            update_quant = int(row[2]) - q
            row = int(row[0]) + 1
            col = 3
            ws_shop_update.update_cell(row, col, update_quant)


def restock():
    """
    Read the restock values from the restock_shop google spreadsheet.
    """
    restock_shop = Restock()

    default_stock = SHEET.worksheet('restock_shop').get_all_values()
    for row in default_stock:
        product = RestockOrder(int(row[0]), row[1], int(row[2]))
        restock_shop.order.append(product)

    return restock_shop


def default_shop(r_s, s_s):
    """
    Restock shop shelves and update current_stock spreadsheet.
    Stock quantityies are set to default values to indicate shelves
    are fully stocked.
    Update the shop balance as these items are purchased
    from wholesaler at a reduced price of 70% of sale price.
    """
    ws_shop_update = SHEET.worksheet('current_stock')
    ws_shop = ws_shop_update.get_all_values()
    ws_balance_update = SHEET.worksheet('shop_balance')
    ws_balance = ws_balance_update.get_all_values()

    for rs_q, s_q in zip(r_s.order, s_s.stock):
        stock_required = rs_q.quantity - s_q.quantity
        for row in ws_shop:
            if row[1] == rs_q.name:
                update_quant = int(row[2]) + stock_required
                row = int(row[0]) + 1
                col = 3
                ws_shop_update.update_cell(row, col, update_quant)

        shop_cost = (stock_required * (s_q.price * 0.7))
        s_q.quantity += stock_required
        s_s.balance -= shop_cost

    shop_balance = str(s_s.balance)
    ws_balance_update.update_cell(1, 2, shop_balance)


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
            print(f"CURRENT SHOP BALANCE IS €{round(stock_shop.balance, 2)}")
            print("------------------")
        elif option_sel == "2":
            new_customer_order(stock_shop)
            cust_order = read_customer('customer_order')
            customer_order(cust_order)
            process_customer_order(cust_order, stock_shop)
        elif option_sel == "3":
            print("\n------------------")
            print("RESTOCKING SHOP...")
            r_s = restock()
            default_shop(r_s, stock_shop)
            current_shop_stock(stock_shop)
            print(f"CURRENT SHOP BALANCE IS €{round(stock_shop.balance, 2)}")
            print("------------------")
            print("\nTHE SHOP HAS NOW BEEN RESTOCKED AT WHOLESALE PRICES")
            print("------------------")
        else:
            print("------------------")
            print("THE SHOP DOES NOT PROVIDE THIS SERVICE")
            print("------------------")


def main():
    open_shop()


main()
