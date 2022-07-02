from selenium import webdriver

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    driver.set_window_size(int(step['width']), int(step['height']))
