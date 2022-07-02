from selenium import webdriver
from lib.core import Core

from utils.selector import SelectorType

def handleStep(driver: webdriver, step: dict,memory: dict):
    steps = step['step'] if 'step' in step else []
    instance: Core = memory['instance']
    times = int(step['times'])
    for i in range(times):
        for step in steps:
            instance.runStep(step)


