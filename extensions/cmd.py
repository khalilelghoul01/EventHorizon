import subprocess
from selenium import webdriver

from utils.selector import SelectorType


def handleStep(driver: webdriver, step: dict, memory: dict):
    command = step['command'].strip()
    args = command.split(' ')
    if(len(args) == 0):
        raise Exception('Command is empty')
    try:
        process = subprocess.run(args)
        return process.returncode
    except Exception as e:
        raise Exception(
            f"Error while executing command: {command}\nError: " + str(e))
