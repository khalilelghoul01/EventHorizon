from selenium import webdriver
import time


def handleStep(driver: webdriver, step: dict, memory: dict):
    timeToSleep = int(step['time'])
    time.sleep(timeToSleep)
