from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import csv

# Set up the webdriver (using Chrome in this example)
driver = webdriver.Chrome()

# Open a website (Google in this example)
driver.get("https://fantasy.espn.com/football/players/projections?leagueFormatId=1")

players_list = []

while True:
    # Wait for the loader to disappear (if present) before clicking the next button
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "loader"))
    )    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "full-projection-table"))
    )
    players = driver.find_elements(By.CLASS_NAME, "full-projection-table")
    for player in players:
        player_outlook_element = player.find_element(By.CLASS_NAME, "full-projection-player-outlook__content")
        player_outlook = player_outlook_element.text if player_outlook_element else ""

        if player_outlook == "No outlook available.":
            continue    

        player_name_link = player.find_element(By.CLASS_NAME, "pointer")
        player_name = player_name_link.text if player_name_link else ""

        player_outlook_title_element = player.find_element(By.CLASS_NAME, "full-projection-player-outlook__title")
        player_outlook_week = player_outlook_title_element.text.split()[1] if player_outlook_title_element else  ""
        player_teamname_element = player.find_element(By.CLASS_NAME, "player-teamname")
        player_teamname = player_teamname_element.text if player_teamname_element else ""

        player_position_element = player.find_element(By.CLASS_NAME, "position-eligibility")
        player_position = player_position_element.text if player_position_element else ""

        players_list.append({
            "name": player_name,
            "team": player_teamname,
            "position": player_position,
            "week": player_outlook_week, 
            "outlook": player_outlook
        })     

    # Find the next button and click it if it's not disabled
    next_button = driver.find_element(By.CLASS_NAME, "Pagination__Button--next")
    if next_button.get_attribute("disabled"):
        break
    next_button.click()

# Close the browser
driver.quit()      

# Get the header from the keys of the first dictionary
header = players_list[0].keys()

csv_file_name = "player_outlooks.csv"

# Write the data to CSV
with open(csv_file_name, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=header)
    
    # Write header
    writer.writeheader()
    
    # Write data rows
    writer.writerows(players_list)