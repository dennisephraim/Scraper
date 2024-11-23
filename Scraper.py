from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

import time

# get the profiles on the current page

def extract_profiles_info(driver):
    # target the element containing the info
    profiles_text = []

    profiles = driver.find_element(By.XPATH, '//*[@id="directory-search"]/div[6]')

    # resorting to using beautiful soup because of the parsing
    src = profiles.get_attribute("innerHTML")
    soup = BeautifulSoup(src, "html.parser")

    cols = [
        "Name",
        "BCD",
        "Email Address",
        "Organization",
        "Street",
        "City",
        "Phone",
        "Website",
        "Degree Held",
        "Age Group Served",
        "Focus of Practice",
        "Modalities",
        "BCD Specialty Certification Held 1",
        "BCD Specialty Certification Held 2",
        "BCD Specialty Certification Held 3",
    ]

    for contact in soup.find_all(class_="ds-contact-name"):
        item_list = []

        # there are 15 entries for person.
        # print(len(contact.find_all("span", {"class":"ng-scope"})))

        for i, item in enumerate(contact.find_all("span", {"class": "ng-scope"})):
            # print(item.text)
            if ("BCD Specialty Certification Held") in item.text:
                item_list.append(item.text.replace(cols[i][:-2], "").strip())
            else:
                item_list.append(item.text.replace(cols[i], "").strip())

        profiles_text.append(item_list)

    # store in a dataframe.
    df = pd.DataFrame(profiles_text, columns=cols)

    return df


def main(driver):
    print("Opening webpage")
    driver.get(
        "https://www.abcsw.org/index.php?option=com_mcdirectorysearch&view=search&id=2001997#/"
    )
    title = driver.title
    print(title)

    # find the search button, wait for it to be visible first...
    search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="directory-search"]/div[3]/div/form/div[9]/a[2]')
        )
    )
    # Click the search button
    search_button.click()

    # sleep abit and let's start scraping...
    time.sleep(30)
    scrape_page_limit = 2
    page_num = 0
    dfs = []

    while page_num != scrape_page_limit:
        print(f"Scraping from page: {page_num}")

        df = extract_profiles_info(driver)
        dfs.append(df)
        # find the next button
        next_page_button = driver.find_element(By.XPATH, '//*[@id="next"]')
        time.sleep(10)
        # go to the next page
        page_num+=1
        next_page_button.click()

    print("Completed!!")
    final = pd.concat(dfs, ignore_index=True)
    final.to_csv("results.csv")

    driver.quit()


if __name__ == "__main__":
    options = Options()
    # options.add_experimental_option("detach", True)
    
    # this disables the browser view!!!
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    main(driver)