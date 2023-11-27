import os
import json
import argparse
import pandas as pd
from time import sleep
from selenium import webdriver
from bs4 import BeautifulSoup
from soup_parser import SoupContentParser

class Parser:

    def __init__(self, driver):
        self.driver = driver
        self.soup_parser = SoupContentParser(driver)  # Pass the driver to SoupContentParser

    def parse_data(self, hrefs, type_org):
        self.driver.maximize_window()
        self.driver.get('https://www.goldenpages.uz')
        org_id = 0
        outputs = []

        for organization_url in hrefs:
            try:
                self.driver.get(organization_url)
                sleep(3)
                soup = BeautifulSoup(self.driver.page_source, "lxml")
                org_id += 1
                name = self.soup_parser.get_name(soup)
                address = self.soup_parser.get_address(soup)
                gpage = self.driver.current_url
                phone = self.soup_parser.get_phone(soup)
                output_data = {
                    "No": org_id,
                    "Name": name,
                    "Address": address,
                    "GoldenPage": gpage,
                    "Phone": phone,
                }

                outputs.append(output_data)

                print(f'Данные добавлены, id - {org_id}')

                sleep(1)
            except Exception as e:
                print('Exception:', e)

        # Save all data to an Excel file
        df = pd.DataFrame(outputs)
        df.to_excel(f'src/output/{type_org}_outputs.xlsx', index=False)

        print('Данные сохранены')
        self.driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("type_org", help="organization type")
    args = parser.parse_args()
    type_org = args.type_org

    all_hrefs = []
    files = os.listdir(f'src/links/{type_org}')
    for file in files:
        with open(f'src/links/{type_org}/{file}', 'r', encoding='utf-8') as f:
            hrefs = json.load(f)['links']
            all_hrefs += hrefs
    all_hrefs = list(set(all_hrefs))
    print('all_hrefs', len(all_hrefs))

    driver = webdriver.Chrome()
    parser = Parser(driver)
    parser.parse_data(all_hrefs, type_org)
