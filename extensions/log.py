from selenium import webdriver


def handleStep(driver: webdriver, step: dict, memory: dict):
    print(f"{step['msg']}")
