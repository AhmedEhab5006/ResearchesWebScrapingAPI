from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def click_recaptcha_checkbox(driver, timeout=10):
    try:
        wait = WebDriverWait(driver, timeout)

        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="reCAPTCHA"]'))
        )

        driver.switch_to.frame(iframe)
        time.sleep(1)

        checkbox = wait.until(
            EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
        )
        checkbox.click()

        time.sleep(1)
        driver.switch_to.default_content()

        return True

    except Exception as e:
        print(f"[reCAPTCHA] Not found or failed: {e}")
        driver.switch_to.default_content()
        return False