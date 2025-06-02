from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

EMAILFIELD = (By.ID, "i0116")
PASSWORDFIELD = (By.ID, "i0118")
NEXTBUTTON = (By.ID, "idSIButton9")


def handle_microsoft_auth(
    driver: WebDriver, microsoft_mail: str, microsoft_password: str
):
    try:
        # wait for email field and enter email
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(EMAILFIELD)
        ).send_keys(microsoft_mail)
        # Click Next
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
    except:
        # might happen when browser remembres you'r mail
        pass

    # wait for password field and enter password
    WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable(PASSWORDFIELD)
    ).send_keys(microsoft_password)

    # Click Login
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable(NEXTBUTTON)).click()

    # for two fuctor authentication
    # Click 'Call' as identity verification method
    WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@data-value='TwoWayVoiceMobile']"))
    ).click()

    # Click 'Yes' for "Stay signed in?"
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable(NEXTBUTTON)).click()
