'''
Scrapes https://www.lounaat.info/<address-city> for lunch menus of today. 
'''
import pandas as pd

import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def get_menu_list(url):
    # Create ChromeOptions object to set up headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options = chrome_options)
    driver.get(url)


    # number of times to press TAB. This is used to navigate through cookies on the site
    N = 3  

    actions = ActionChains(driver) 
    for _ in range(N):
        actions = actions.send_keys(Keys.TAB)

    # Accept cookies
    actions = actions.send_keys(Keys.ENTER)
    actions.perform()

    # Get more restaurants by clicking 'See More'. This is somehow broken but it also isn't that important.
    #driver.find_element(By.CLASS_NAME, 'more.content').click()
    #time.sleep(2)
    #driver.find_element(By.CLASS_NAME, 'more.content').click()
    #time.sleep(2)

    restaurant_divs = driver.find_elements(By.XPATH, "//div[contains(text(), menu.item.category-)]")

    # Create an empty list to store the text or attributes of the child divs
    result_list = list()

    # Iterate through the child div elements and extract information
    for div in restaurant_divs:
        if 'menu item category' in div.get_attribute('class'):
            result_list.append(div.text)
    # Check if result_list is empty and exit with an error message if true
    if not result_list:
        print(f"Error: No restaurants found, check input; perhaps the location ({url.split('/')[-1]}) you've provided is incorrect?\nExpected format is <address>-<city>")
        sys.exit(1) 
    driver.quit()

    return result_list

# Define a function to convert distances to meters
def convert_to_meters(distance_str):
    distance_numeric = int(''.join(filter(str.isdigit, distance_str)))
    return distance_numeric * 1000 if 'km' in distance_str.lower() else distance_numeric


def clean_menu_list(result_list):
    '''
    Exclude student restaurants and drop ratings. Clean distances into meters in numeric form
    '''
    restaurants = []
    for setti in result_list:
        setti = setti.split('\n')
        # Exclude student restaurants
        if 'unica' not in setti[0].lower() and 'kårkafé' not in setti[0].lower():
            restaurants.append(setti)
    restaurants = [[item for item in sublist if not (any(char.isdigit() for char in item) and '/' in item)] for sublist in restaurants]
    restaurants = [[*sublist[:-1], convert_to_meters(sublist[-1])] for sublist in restaurants]
    return restaurants

def create_df(result_list):
    restaurants = list()
    distances = list()
    open_hours = list()
    menu = list()

    for setti in result_list:
        restaurants.append(setti[0])
        distances.append(setti[-1])
        open_hours.append(setti[1])
        menu.append(setti[2:-1])

        ravintelit = pd.DataFrame({
        'Ravintola': restaurants,
        'Etäisyys': distances,
        'Aukiolo': open_hours,
        'Menu': menu
        })
    
    return ravintelit


def restaurant_for_the_day(df):
    '''
    Return one random restaurant and its contents from the DataFrame
    '''
    return df.sample(1)


#print(clean_menu_list(get_menu_list(URL)))