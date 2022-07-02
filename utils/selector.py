import re
from selenium.webdriver.common.by import By


def SelectorType(selector: str) -> str:
    # match xpath
    if re.match(r'^(//|\.//|\.\.//|\.\.\.//)|(/|\./|\.\./|\.\.\./).*', selector):
        return By.XPATH
    else:
        return By.CSS_SELECTOR
