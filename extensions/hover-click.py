from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    selector = step['selector']
    hoverSelector = step['hoverSelector']
    element = driver.find_elements(SelectorType(selector), selector)
    elementHover = driver.find_elements(SelectorType(hoverSelector), selector)
    if len(element) == 0:
        raise Exception('Element not found: ' + selector)

    if len(elementHover) == 0:
        raise Exception('Element not found: ' + hoverSelector)
    element = element[0]
    elementHover = elementHover[0]
    Hover = ActionChains(driver).move_to_element(
        elementHover).move_to_element(element)
    Hover.click().build().perform()
