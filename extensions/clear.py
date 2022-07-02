from selenium import webdriver

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    selector = step['selector']
    if not 'element' in step:
        element = driver.find_elements(SelectorType(selector), selector)
        if len(element) == 0:
            raise Exception('Element not found: ' + selector)
        element = element[0]
    else:
        element = step['element']
    element.clear()
