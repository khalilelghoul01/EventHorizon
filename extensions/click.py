from selenium import webdriver
from utils.selector import SelectorType
from selenium.webdriver.common.action_chains import ActionChains


def handleStep(driver: webdriver, step: dict, memory: dict):
    selector = step['selector']
    if not 'element' in step:
        element = driver.find_elements(SelectorType(selector), selector)
        if len(element) == 0:
            raise Exception('Element not found: ' + selector)
        element = element[0]
    else:
        element = step['element']
    try:
        element.click()
    except Exception as e:
        raise Exception('Element not clickable: ' + selector)
        # print("using action chains")
        # js = "try {return document.evaluate('##selector##', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;}catch (error) { return null; }".replace(
        #     '##selector##', selector)
        # element = driver.execute_script(js)
        # if element is None:
        #     raise Exception('Element not found or not clickable: ' + selector)
        # js = "try { arguments[0].click() }catch (error) { return null; }"
        # driver.execute_script(js, element)
