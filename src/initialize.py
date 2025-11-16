import pickle
from time import sleep

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

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
    if config.browser_installed == "firefox":
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    elif config.browser_installed == "firefox":
        options = ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    else:
        raise ValueError("unknown browser installed")

    driver.get("https://one.prat.idf.il/login")

    # loading cookies
    if config.cookies_file_path.exists():
        print(f"loading authentication cookies from: {config.cookies_file_path}")
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
        print(f"saving cookies to file: {config.cookies_file_path}")

    print("starting to set future reports")
    handle_set_future_reports(driver=driver)
    print("successfully set future reports")

    driver.close()
    print("program ended")
