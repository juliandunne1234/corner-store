<h1 align="center">Corner Store</h1>
<p>A very small shop on the corner of an estate where a person can get basic items when needed. The shop window opens to accept customer orders and it is also possible to phone ahead and give your order so it is ready for collection. When the shop stock is running low the shopkeeper can restock the shop at discounted wholesale prices.

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
* Selecting option 1 returns the current shop balance a list of the items available and quantities in stock in the shop.
![Shop open](/images/option-1-full-stock.jpg)

***

### Option-2 Enter Customer Order
* Selecting option 2 prompts the customer to enter their name, amount of euros they hold and the items and quantity of items they require.
![Shop open](/images/option-2-enter-order.jpg)
* Programme then returns this order and the parts of the order that could be executed.
![Shop open](/images/option-2-execute-order.jpg)
* If the shop is unable to process any part of the customer order then this is explained to the customer.
![Shop open](/images/unable-to-execute.jpg)
***

### Option-3 Execute Existing Order
* Selecting option 3 executes an order that is to be ready for a customer to collect. The shop balance and stock are updated accordingly.
![Shop open](/images/option-3-execute-existing-order.jpg)
***

### Option-4 Restock Shop
* Selecting option 4 restocks the shop. The shop inventory levels are returned to the opening amounts however the shop must pay to restock the shop albeit at the lower wholesale prices.
![Shop open](/images/option-4-restock-shop-at-wholesale-price.jpg)
***

## Testing
* Testing to confirm shop functions as intended. This included:
    * If option 1-4 is not selected then the shop should close as it does not provide that service.
    * Shop requires customer to enter a number for euros that they hold.
    * If a customer requests items that the shop does not stock then the customer is reminded that only the items in stock are available.
    * When an item is purchased the stock quantity reduces and the customer cash and also the shop balance are updated to reflect this purchase.
    * When shop stock is depleted the shopkeeper can restock the shop whereby the shop balance is updated to reflect this albeit at the lower wholesale prices.S
***

## Validator Testing
* Python code - all warnings have been resolved except for two that appear multiple times when passing the run.py file content through the [pep8 online validator](http://pep8online.com/)
    * E701: multiple statements on one line(colon)
    * W291: trailing whitespace
* Neither of the above errors impact running of the corner store python app.

## Deployment
* The corner store python app has been deployed to [Heroku](https://www.heroku.com/) - a cloud platform service for developers to build and run applications: 
    * Live link - [Corner Store](https://corner-store-app.herokuapp.com/)
***

## Credits
* The Love-Sandwiches walkthrough project with Code Institute was very helpful to use as a starting point for this project.
* Tutor support was also very helpful and advice taken from mentor sessions was used during development of the app
* Online resources including [python documenation](https://docs.python.org/3/library/dataclasses.html) for creating dataclasses