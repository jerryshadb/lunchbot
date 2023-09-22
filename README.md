author: Jerry Shadbolt
e-mail: jerry.shadbolt@windowslive.com

Web scraper project to learn Selenium and web scraping. Created this in order to automate the tedious process of picking where to eat lunch with co-workers.

Usage: 
Go to project folder and run main.py with parameters current_time and distance. So python3 main.py 12 500

current_time specifies the time of day you want to get weather info for. Weather is read, by default, for the current day at 00:00:00 onwards. Timezones not handled. distance is the radius of restaurants you want to include. I'm not entirely certain how the browser distance functionality works so proceed with caution but I believe it should be more or less ok. 
