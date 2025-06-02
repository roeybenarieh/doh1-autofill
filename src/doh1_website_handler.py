from time import sleep

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

IDFIELD = (By.CLASS_NAME, "formControl")
GENERALNEXTBUTTON = (By.CLASS_NAME, "btnGeneral.send")

# set future report
FUTUREREPORTSBUTTON = (By.CLASS_NAME, "finishReportBtn")
CALENDAR = (By.CLASS_NAME, "react-calendar__month-view__days")
BUTTONSELEMENTS = (By.TAG_NAME, "button")
BASISIMAGE = (By.XPATH, "//img[contains(@src, 'basis')]")
PRESENTBUTTON = (By.CLASS_NAME, "radioTextRow")
SENDREPORTBUTTON = (By.CLASS_NAME, "radioTextRow")


def suppress(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except:
        return None


def handler_doh1_without_cookie(driver: WebDriver, id_number: str):
    # wait for the id field and enter id
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(IDFIELD)).send_keys(
        id_number
    )
    # click next
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(GENERALNEXTBUTTON)
    ).click()


def handle_set_future_reports(driver: WebDriver):
    # set future reports to be in military base

    # click on future reports button
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(FUTUREREPORTSBUTTON)
    ).click()

    # get calendar days(each day is a button)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(CALENDAR)
    )  # wait for calendar to load
    # HACK: since I dont know how many buttons I should wait for
    sleep(10)

    while True:
        calendar = driver.find_element(*CALENDAR)
        day_buttons = calendar.find_elements(*BUTTONSELEMENTS)
        reportable_days_buttons = [
            day_button for day_button in day_buttons if day_button.is_enabled()
        ]
        none_reported_days_buttons = [
            day_button
            for day_button in reportable_days_buttons
            if not suppress(day_button.find_element, By.CLASS_NAME, "hasReport")
        ]
        if not none_reported_days_buttons:
            break

        # report the day
        for day in none_reported_days_buttons:
            day.click()
            # Click basis image
            WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable(BASISIMAGE)
            ).click()

            # Click 'present' button
            WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable(PRESENTBUTTON)
            ).click()

            # Click 'send report'
            WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable(GENERALNEXTBUTTON)
            ).click()

            # Click 'ok and finish'
            WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable(GENERALNEXTBUTTON)
            ).click()
