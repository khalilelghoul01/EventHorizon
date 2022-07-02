from selenium import webdriver


def handleStep(driver: webdriver, step: dict, memory: dict):
    driver.get(step['url'])
    return step['url']
