from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SoupContentParser:
    def __init__(self, driver):
        self.driver = driver

    def get_phone(self, soup_content):
        try:

            phone_button = self.driver.find_element(By.XPATH, "//button[contains(text(),'Показать номер')]")
            phone_button.click()

            print("Clicked the button to reveal phone number")

            phone_link = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'gp_phoneList')]//a[contains(@href, 'tel:')]"))
            )

            print("Phone number element is present")

            phone = phone_link.text.strip()

            print(f"Extracted phone: {phone}")

            return phone
        except Exception as e:
            print(f"Error extracting phone number: {e}")
            return ""

    def get_name(self, soup_content):
        try:
            name = soup_content.find("h1", {"class": "h3"}).getText().strip()
            return name
        except Exception:
            return ""

    def get_address(self, soup_content):
        try:
            # Find the parent div with class "gp_wrap_address"
            address_div = soup_content.find("div", class_="gp_wrap_address")

            # Extract the text within the address div
            address_text = address_div.get_text(strip=True)

            address_text = address_text.replace("Ориентиры:", "\nОриентиры:")

            return address_text
        except Exception as e:
            print(f"Error extracting address: {e}")
            return ""

    def get_landmarks(self, soup_content):
        try:
            landmarks_div = soup_content.find("ul", {"class": "gp_landmark"})
            landmarks = [landmark.getText().strip() for landmark in landmarks_div.find_all("li")]
            return landmarks
        except Exception:
            return []
