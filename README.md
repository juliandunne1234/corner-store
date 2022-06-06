<h1 align="center">Corner Store</h1>
<p>As everything goes online, even the local corner shop at some point will stop accepting cash. The idea behind this app is that as the customer enters the shop they will enter their details upon which their account balance will be displayed. The customer will then top up their account credit and order the items and quantity that they require. After each purchase the customer credit reduces and the shop balance increase as a result or the purchased items. When the shop stock is running low the shopkeeper can restock the shop at discounted wholesale prices. The shop functions the same as any other corner store it just no longer accepts cash.

Created as part of the Code Institue Portfolio 3: Python Essentials Milestone Project 

Live link - [Corner Store](https://corner-store-app.herokuapp.com/)
</p>

***

## Table of Contents
* [Features](#Features)
* [Testing](#Testing)
* [Validator Testing](#validator-testing)
* [Deployment](#Deployment)
* [Credits](#Credits)
***

## Features 
* Running the program in the heroku-app starts with the shop opening to give 4 possible options:
![Shop open](/images/open-shop.jpg)

### Option-1 Current Shop Stock
* Selecting option 1 returns the shop stock including the product ID#, product name and the quantity in stock. These values are taken from the current_stock google spreadsheet.
![Shop open](/images/gspread_current_stock.jpg)
* The app displays the current shop balance a list of the items available and quantities in stock in the shop. Price is not included.
![Shop open](/images/option-1-full-stock.jpg)

***

### Option-2 Enter Customer Order
* Selecting option 2 prompts the customer to enter their name and the amount they want to top up their account credit by. The shop stock list is also returned to help with the users selection.
![Shop open](/images/option-2-enter-cust-details.jpg)
* The customer then enters the items required and the quantity of each item required. Items are selected by entering the ID#.
![Shop open](/images/option-2-enter-order.jpg)
* The app then returns the customer order and the item and quantities that have been purchased.
![Shop open](/images/option-2-execute-order.jpg)
* The current_stock and shop_balance google spreadsheets are also updated so that the database remains up to date.
![Shop open](/images/update_current_stock.jpg)
* If the shop is unable to process the customer order as a item that is not listed is selected then this is explained to the customer.
![Shop open](/images/unable-to-execute.jpg)
* If the customer order is invalid due the customer is notified and the shop returns to the shop menu.
![Shop open](/images/invalid-order-entry.jpg)
***

### Option-3 Restock Shop
* Selecting option 3 restocks the shop using the default stock inventory values from the restock_shop google spreadsheet.
![Shop open](/images/gspread_restock_shop.jpg)
* The shop inventory levels are returned to the opening amounts however the shop must pay to restock the shop at the lower wholesale prices.
![Shop open](/images/option-3-restock-shop.jpg)
* The current_stock and shop_balance google spreadsheets are updated so that the database remains up to date.
***

## Testing
* Testing to confirm shop functions as intended. This included:
    * If option 1-3 is not selected then the shop should tell customer it does not provide that service and return to the shop menu.
    * Shop requires customer to enter a number for euros that they hold.
    * When an item is purchased the stock quantity reduces and the customer credit and the shop balance are updated to reflect this purchase. The stock quantities also reduce.
    * The google spreadsheets are also sent this information so that the database remains up to date
    * If a customer requests items that the shop does not stock then the customer is reminded that only the items in stock are available.
    * When shop stock is depleted the shopkeeper can restock the shop whereby the shop balance is updated to reflect this albeit at the lower wholesale prices.
    * The google spreadsheets are also sent this information so that the database remains up to date
***

## Validator Testing
* Python code - all warnings have been resolved except for one that appears multiple times when passing the run.py file content through the [pep8 online validator](http://pep8online.com/)
    * E701: multiple statements on one line(colon)
* The above error does impact the running of the corner store python app.

## Deployment
* The corner store python app has been deployed to [Heroku](https://www.heroku.com/) - a cloud platform service for developers to build and run applications: 
    * Live link - [Corner Store](https://corner-store-app.herokuapp.com/)
***

## Credits
* The Love-Sandwiches walkthrough project with Code Institute was very helpful to use as a starting point for this project.
* Tutor support was also very helpful and advice taken from mentor sessions was used during development of the app
* Online resources including [python documenation](https://docs.python.org/3/library/dataclasses.html) for creating dataclasses