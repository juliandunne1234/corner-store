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

def open_shop():
    """
    Provide 3 options to the user:
    1) See stock inventory
    2) Input customer order
    3) Complete existing customer order
    """
    print("\t---CORNER STORE---")
    print("\nPlease choose number 1-3 to proceed")
    print("1) Shop consumables and prices")
    print("2) Create new Customer Order")
    print("3) Execute existing costomer order")
    option_sel = input("\nEnter: ")

    if option_sel == "1":
        current_shop_stock()
    elif option_sel == "2":
        print("Test 2")
    elif option_sel == "3":
        print("Test 3")
    else:
        print("The shop does not provide this service")

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

def main():
    open_shop()

main()