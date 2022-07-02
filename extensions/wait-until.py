from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    selector = step['selector']
    time = int(step['time'])
    try:
        element = WebDriverWait(driver, time).until(
            EC.presence_of_element_located((SelectorType(selector), selector))
        )
    except:
        raise Exception('Element not found: ' + selector +
                        'after waiting 10 seconds')
