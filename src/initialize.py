import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from src.config_handler import get_config
from src.doh1_website_handler import (
    handle_set_future_reports,
    handler_doh1_without_cookie,
)
from src.microsoft_auth_handler import handle_microsoft_auth


def run():
    print("starting")
    config = get_config()
    # scraping init
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get("https://one.prat.idf.il/login")

    # loading cookies
    if config.cookies_file_path.exists():
        print("loading authentication cookies from previous runs")
        cookies = pickle.load(open(config.cookies_file_path, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)

        driver.refresh()

    # in case the doh1 cookie isn't working
    try:
        handler_doh1_without_cookie(driver=driver, id_number=config.id_number)
    except:
        pass

    # in case of microsoft authentication cookie isn't working
    if len(driver.window_handles) > 1:
        print("handling microsoft authentication")
        driver.switch_to.window(driver.window_handles[1])
        handle_microsoft_auth(
            driver=driver,
            microsoft_mail=config.microsoft_mail,
            microsoft_password=config.microsoft_password,
        )
        driver.switch_to.window(driver.window_handles[0])

        print("successfully handled microsoft authentication")
        # HACK: wait for cookies to load before writing them to file
        sleep(10)
        pickle.dump(driver.get_cookies(), open(config.cookies_file_path, "wb"))
        print("saving cookies to file")

    print("starting to set future reports")
    handle_set_future_reports(driver=driver)
    print("successfully set future reports")

    driver.close()
    print("program ended")
