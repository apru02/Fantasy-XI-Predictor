from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import pandas as pd

#make global df
df = pd.DataFrame(columns=['player_id','player_name'])


#open csv file to update player name with its id

def get_all_players(country):
    # URL of the webpage
    url = 'http://howstat.com/cricket/Statistics/Players/PlayerCountryList.asp'

    # Create a WebDriver instance (make sure to have ChromeDriver installed)
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get(url)

    time.sleep(2)


    # Set the format to T20 by selecting the option with value "W"
    format_select = Select(driver.find_element('name', 'cboFormat'))
    format_select.select_by_value('W')
    # Wait for 1 sec
    time.sleep(2)

    # Set the country to IND by selecting the option with value "IND"
    country_select = Select(driver.find_element('name', 'cboCountry'))
    country_select.select_by_value(country)
    # Wait for 1 sec
    time.sleep(2)

    # Extract the updated HTML content
    updated_html = driver.page_source

    # Close the WebDriver
    time.sleep(1)
    driver.quit()

    # Parse the updated HTML content
    updated_soup = BeautifulSoup(updated_html, 'html.parser')

    # Extract and print the player names
    player_table = updated_soup.find('table', class_='TableLined')
    rows = player_table.find_all('tr')[1:-1]  # Exclude header and footer rows

    for row in rows:
        columns = row.find_all('td')
        #print the player id which is the last 4 digits of the href
        player_id = columns[0].find('a')['href'][-4:]
        #remove the leading and trailing whitespace
        player_id = player_id.strip()
        player_id = int(player_id)
        #print the player name
        name = columns[0].text
        #remove the leading and trailing whitespace
        name = name.strip()
        if(name[-1] == '*'):
            name = name[:-1]
        #append the player id and player name to the dataframe without append()
        df.loc[len(df.index)] = [player_id,name]

#write the dataframe to csv file//just update the csv file
countries = ['AUS','BAN','ENG','IND','NZL','PAK','SAF','SRL','WIN','ZIM','AFG','IRE']
for country in countries:
    get_all_players(country)

df.to_csv('player_id.csv',mode='a',index=False)

    

    
    
