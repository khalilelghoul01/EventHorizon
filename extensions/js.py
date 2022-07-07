from selenium import webdriver
import re
from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    path = step['path'] if 'path' in step else None
    code = step['[text]'] if '[text]' in step else None

    if path is None and code is None:
        raise Exception('No path or code specified')
    if path is not None:
        with open(path) as f:
            codejs = f.read()
        if codejs.strip() == '':
            raise Exception('Empty code')
        return driver.execute_script(codejs)
    elif code is not None:
        if code.strip() == '':
            raise Exception('Empty code')
        return driver.execute_script(code)
