# Motivation behind sel_crawler
* To get familiar with selenium
* To better understand how web crawlers operate, in particular 'stock grabbers'

# Disclaimer
* This package has been created purely for educational purposes
* Do NOT rely on this package to grab stock.
* It's heavily reliant on individual html elements to be in specific positions. It is almost bound to break whenever a website updates.

# Features
* Sit and refresh on a page until stock becomes available.
* If stock becomes available, "grab" the stock with your details.
* Notifies you when stock becomes available. (optional)

# Missing Features
* IP Rotation
* Humanlike interactions with the web page.
* Truly random web refreshes.
* Solving bot detection puzzles.

# The Main API

## websites module (sel_crawler/core/websites.py)
This is the main module where the logic behind each individual website resides.
## personal_details module (sel_crawler/core/personal_details.py)
This is where you initialise your data, so that the program can actually buy the stock using your details once it becomes available.
## sel_crawler/core/notifications
All the modules relating to notification systems reside here.
## sel_crawler/core/screenshots
Upon "success", screenshot is sent here.
## multi_instance.py sel_crawler/multi_instance
Utilise multithreading to run many webcrawlers concurrently. Take care with this setting.

# Example Usage for one web crawler 

```python
from sel_crawler.core.websites import Game
from sel_crawler.core.personal_details import ContactDetails, PaymentDetails

# Initialisation of variables
PATH = "C:\Program Files (x86)\Web Drivers\chrome_webdriver\chromedriver.exe"
contact = ContactDetails("James","Marathon","cx@yz.co.uk","07515365978","AB11 4ZZZ","1","Cecilia Palace","Jim County", "London")
payment = PaymentDetails("VISA","4485051377032585","Mr James Marathon","08/15","331")

# Pass details to the main class
game_scraper =Game(PATH, contact, payment)
# start the scraper
game_scraper.main('https://www.game.co.uk/playstation-5')
```

# Example Usage with >1 web crawler

```python
from sel_crawler.core.websites import Game, Argos
from sel_crawler.core.personal_details import ContactDetails, PaymentDetails, LoginDetails
from sel_crawler.multi_instance import MultiInstance

# Initialisation of variables
PATH = "C:\Program Files (x86)\Web Drivers\chrome_webdriver\chromedriver.exe"
contact = ContactDetails("James","Marathon","cx@yz.co.uk","07515365978","AB11 4ZZ","1","Cecilia Palace","Jim County", "London")
payment = PaymentDetails("VISA","4485051377032585","Mr James Marathon","08/15","331")
# Argos requires login for checkout
login = LoginDetails('cx@yz.co.uk','pw321')

# Instance 1
game_scraper = Game(PATH, contact, payment)
# Instance 2
argos_scraper = Argos(PATH, contact, payment, login)

# WWE disc from game & TV from argos
multi = {game_scraper:'https://www.game.co.uk/en/wwe-2k22-2876111',\
     argos_scraper: 'https://www.argos.co.uk/product/9489237'}
# crawl both
x = MultiInstance(multi)
x.multi_scrape()
```



