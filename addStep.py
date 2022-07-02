import json
import os
import sys

with open('./config/steps.json') as configFile:
    config = json.load(configFile)
config = config[0]
args = sys.argv

if(len(args) != 2):
    print("Usage: python addStep.py <step_name>")
    sys.exit()


step_name = args[1]
data = {
    "paramaters": [
    ],
    "description": "description",
    "file": step_name
}

if step_name in config:
    print("Step already exists.")
else:
    config[step_name] = data
    config = [config]
    with open('./config/steps.json', 'w') as configFile:
        json.dump(config, configFile, indent=4)
    print("Step added.")

# exist file
if os.path.isfile('./steps/'+step_name+'.py'):
    print("Step file already exists.")
    sys.exit()


code = """from selenium import webdriver

from utils.selector import SelectorType

def handleStep(driver: webdriver, step: dict,memory: dict):
    pass

"""
with open("extensions/"+step_name+".py", "w") as f:
    f.write(code)
