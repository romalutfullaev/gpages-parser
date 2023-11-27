import os
import json
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup


class LinkParser:

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, by, value):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logging.error(f"Timeout waiting for element: {value}")
            return None

    def scrape_links(self, target_url, rubric_id):
        all_links = set()

        page_number = 1
        while True:
            url = f'{target_url}?Id={rubric_id}&Page={page_number}'
            self.driver.get(url)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            link_divs = soup.find_all('div', class_='h3 mb-0')
            links = {f"https://www.goldenpages.uz{div.find('a')['href']}" for div in link_divs}

            if not links:
                break

            all_links.update(links)

            next_link = self.wait_for_element(By.XPATH, f"//a[@href='/rubrics/?Id={rubric_id}&Page={page_number + 1}']")
            if next_link:
                actions = ActionChains(self.driver)
                actions.move_to_element(next_link).perform()
                next_link.click()
            else:
                break

            page_number += 1

        return list(all_links)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("rubric_id", type=int, help="Rubric ID")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode")
    args = parser.parse_args()

    chrome_options = webdriver.ChromeOptions()
    if args.headless:
        chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    parser = LinkParser(driver)

    target_url = 'https://www.goldenpages.uz/rubrics/'

    rubric_id = args.rubric_id

    try:
        links = parser.scrape_links(target_url, rubric_id)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        driver.quit()
        exit(1)

    folder_path = f'src/links/{rubric_id}'
    os.makedirs(folder_path, exist_ok=True)
    file_name = f'{rubric_id}.json'
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({"links": links}, f, ensure_ascii=False, indent=4)

    driver.quit()
