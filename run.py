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

def open_and_stock_shop():
    create_shop_stock = SHEET.worksheet('restock').get_all_values()
    starting_stock = SHEET.worksheet('current_stock')
    starting_stock.clear()
    for row in create_shop_stock:
        starting_stock.append_row(row)
    print("------------------")


def current_shop_stock():
    """
    Displays list of items on sale and individual price
    """
    print("\n------------------")
    print("Items are available at the following prices")
    print("------------------")
    shop_stock = SHEET.worksheet('current_stock').get_all_values()
    for item in shop_stock:
        print(f'{item[0]} : €{item[2]}')
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
    customer_balance = float(input("Please enter your cash balance: €"))

    worksheet_to_update.append_row([customer_name, customer_balance])

    while True:
        item_order = input("Please select item from shop stock: ")
        item_quantity = int(input("Please enter the amount you want: "))
        worksheet_to_update.append_row([item_order, item_quantity])

        shopping_complete = input("Is there anything else? Y/N\n")
        if shopping_complete == "Y":
            continue
        elif shopping_complete == "N":
            break
        else:
            last_chance = input("Please select Y or N\nIs there anything else we can get you?\n")
            if last_chance != "Y":
                print("We will take that as a no.")
                break

def process_customer_order(worksheet):
    """
    Process a new or existing customer order.
    Only process valid orders where the item
    is in stock in the shop.
    Orders can only be executed based on the
    quantities in stock.
    """
    process_order = SHEET.worksheet(worksheet).get_all_values()
    processing_order = process_order[1:]

    current_stock = SHEET.worksheet('current_stock').get_all_values()
    
    for cust_item in processing_order:
        for stock_item in current_stock:
            if cust_item[0] == stock_item[0]:
                print(cust_item[1])
                print(stock_item[1])
                print(stock_item[2])


def open_shop():
    """
    Provide 3 options to the user:
    1) See stock inventory
    2) Input customer order
    3) Complete existing customer order
    """
    stock_shop = open_and_stock_shop()

    while True:
        print("\t---CORNER STORE---")
        print("\nPlease choose number 1-3 to proceed")
        print("1) Shop consumables and prices")
        print("2) Create new Customer Order")
        print("3) Execute existing costomer order")
        option_sel = input("\nEnter: ")

        if option_sel == "1":
            current_shop_stock()
        elif option_sel == "2":
            new_customer_order()
            process_customer_order('customer_order')
        elif option_sel == "3":
            print("Test 3")
        else:
            print("The shop does not provide this service")
            break

def main():
    open_shop()

main()