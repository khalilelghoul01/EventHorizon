from selenium import webdriver


def handleStep(driver: webdriver, step: dict, memory: dict):
    return {'type': 'var', 'value': step['value'], 'name': step['name']}
