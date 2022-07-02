from selenium import webdriver

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    capture_path = step['path']
    driver.save_screenshot(capture_path)
