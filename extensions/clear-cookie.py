from selenium import webdriver

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    driver.delete_all_cookies()