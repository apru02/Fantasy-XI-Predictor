from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_player_id(player_name):
    # Create a WebDriver instance (make sure to have ChromeDriver installed)
    driver = webdriver.Chrome()

    # Open the webpage
    driver.get('http://howstat.com/cricket/Statistics/Players/PlayerMenu.asp')

    try:
        # Find the input field and enter the player name
        player_input = driver.find_element(By.ID, 'txtPlayer')
        player_input.send_keys(player_name)

        # Find and click the 'Find' button
        find_button = driver.find_element(By.NAME, 'btnFindPlayer')
        find_button.click()

        try:
            # Wait for either the table or the 'No records exist' message to appear
            element_present = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'TableLined')) or
                EC.presence_of_element_located((By.CLASS_NAME, 'TextCrimson10'))
            )

            # Check if the 'No records exist' message is present
            if driver.find_elements(By.CLASS_NAME, 'TextCrimson10'):
                td = driver.find_element(By.CLASS_NAME, 'TextCrimson10')
                if "No player names found matching the text entered. " in td.text:
                    #print("No records exist for the selected criteria")
                    return "0001"

            # Extract and return the player ID from the 2nd row of the table
            rows = driver.find_elements(By.CSS_SELECTOR, '.TableLined tr')
            a_tag = rows[1].find_element(By.TAG_NAME, 'a')
            href = a_tag.get_attribute('href')
            player_id = href[-4:]
            return player_id
        except:
            # Handle the case when neither the table nor the 'No records exist' message is found within the timeout
            #print("Table or 'No records exist' message not found within the timeout. Returning default value '0001'.")
            return "0001"

    finally:
        # Close the WebDriver
        driver.quit()

# print(get_player_id("Bumrah"))