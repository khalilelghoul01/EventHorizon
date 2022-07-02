import re
import psutil
import json
import os
import sys
import time
from lib.args import handleArgs
from lib.timer import Timer
import lib.xmlCore as xml
from selenium import webdriver
import importlib
import configparser

config_syntax = r"\[[ ]*([a-zA-Z0-9_]+)[ ]*(>[ ]*[a-zA-Z0-9_]+[ ]*)*\]"

colors = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'purple': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'reset': '\033[0m'
}

notToLog = ['var']


class Core:

    def __init__(self):
        self.memory = {}
        self.extensions = {}
        self.reports = []
        self.configMap = []
        args = handleArgs()
        self.scenarios = self.loadScenarios(args['senarios'])
        self.browser = args['browser'] if args['browser'] else 'chrome'
        self.report = args['report'] if args['report'] else 'report.json'
        self.remote = args['remote'] if args['remote'] else None
        self.maximize = args['maximize'] if args['maximize'] else None
        self.headless = args['headless'] if args['headless'] else None
        self.driver = None
        try:
            self.driver = self.loadDriver()
        except Exception as e:
            self.saveReport()
            self.logError(e)

    def start(self):
        self.config = self.loadConfig()
        self.currentScenario = None
        self.currentStep = None
        self.currentScenarioTime = 0
        self.currentStepTime = 0
        self.currentReportScenario = {}
        self.run()
        self.saveReport()
        self.driver.close()
        self.driver.quit()

    def stop(self):
        if(self.driver):
            self.driver.close()
            self.driver.quit()
        self.saveReport()
        sys.exit(0)
        return

    def loadScenarios(self, path):
        files = [f for f in os.listdir(path) if f.endswith('.xml')]
        scenarios = []
        for file in files:
            scenario = {
                'filename': file
            }
            file_path = os.path.join(path, file)
            scenario['scenario'] = xml.load_xml(file_path)
            scenarios.append(scenario)
        return scenarios

    def loadDriver(self):
        options = webdriver.ChromeOptions()
        if(self.maximize):
            options.add_argument('--start-maximized')
        if(self.headless):
            options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.remote is None:
            if self.browser == 'chrome':
                return webdriver.Chrome(options=options)
            elif self.browser == 'firefox':
                return webdriver.Firefox()
            elif self.browser == 'ie':
                return webdriver.Ie()
            else:
                return webdriver.Chrome(options=options)
        else:
            time.sleep(3)
            if(self.browser == 'chrome'):
                return webdriver.Remote(
                    command_executor=self.remote,
                    desired_capabilities=webdriver.DesiredCapabilities.CHROME)
            elif(self.browser == 'firefox'):
                return webdriver.Remote(
                    command_executor=self.remote,
                    desired_capabilities=webdriver.DesiredCapabilities.FIREFOX)
            elif(self.browser == 'ie'):
                return webdriver.Remote(
                    command_executor=self.remote,
                    desired_capabilities=webdriver.DesiredCapabilities.INTERNETEXPLORER)
            else:
                return webdriver.Remote(
                    command_executor=self.remote,
                    desired_capabilities=webdriver.DesiredCapabilities.CHROME)

    def addScenarioToReport(self):
        scenario = self.currentScenario
        data = {
            "keyword": "Feature",
            "uri": scenario['scenario']['scenario']['name'],
            "name": scenario['scenario']['scenario']['name'],
            "id": scenario['scenario']['scenario']['name'],
            "line": 2,
            "description": "",
            "tags": [],
            "elements": [
                {
                    "keyword": "Scenario",
                    "id": scenario['scenario']['scenario']['name'],
                    "name": scenario['scenario']['scenario']['name'],
                    "line": 4,
                    "description": "",
                    "tags": [],
                    "type": "scenario",
                    "steps": []
                }
            ]
        }
        self.currentReportScenario = data

    def addStepToReport(self):
        step = self.currentStep
        description = self.config[step['key']]['description']
        if('[text]' in step):
            description = step['[text]'].replace('\n', '').strip()
        data = {
            "keyword": "Step",
            "name": description,
            "line": 25,
            "match": {"location": ""},
            "result": {"status": "passed", "duration": self.currentStepTime}
        }
        self.currentReportScenario['elements'][0]['steps'].append(data)

    def addCurrentReportScenario(self):
        self.reports.append(self.currentReportScenario)

    def loadConfigScenario(self):
        scenario = self.currentScenario['scenario']
        if('config' in scenario['scenario']):
            for config in scenario['scenario']['config']:
                if('path' not in config):
                    self.logError('Config path not found')
                    continue
                for path in config['path']:
                    if('name' not in path):
                        self.logError('Config name not found')
                        continue
                    if('link' not in path):
                        self.logError('Config value not found')
                        continue
                    config = configparser.ConfigParser()
                    config.read(f"scenario_config/{path['link']}")
                    self.configMap.append(path['name'])
                    self.memory[path['name']] = config

    def run(self):
        for scenario in self.scenarios:
            self.currentScenario = scenario
            format, error = self.checkScenario()
            if (not format):
                self.log(error, 'red')
                continue
            timerScenario = Timer()
            timerScenario.start()
            self.addScenarioToReport()
            self.runScenario()
            timerScenario.stop()
            self.currentScenarioTime = timerScenario.getTime()
            self.addCurrentReportScenario()

    def runScenario(self):
        self.memory = {}
        self.memory['instance'] = self
        self.loadConfigScenario()
        for step in self.currentScenario['scenario']['scenario']['step']:
            self.currentStep = step
            format, error = self.checkStep()
            if(not format):
                self.addCurrentReportScenario()
                self.saveReport()
                self.logError(error)
            timerStep = Timer()
            timerStep.start()
            try:
                self.runStep()
            except Exception as e:
                timerStep.stop()
                self.currentStepTime = timerStep.getTime()
                self.addStepToReport()
                self.addCurrentReportScenario()
                self.saveReport()
                self.logError(e)
            timerStep.stop()
            self.currentStepTime = timerStep.getTime()
            if(self.currentStep['key'] not in notToLog):
                self.addStepToReport()

    def runStep(self, step=None):
        self.currentStep = self.loadStep(step)
        self.log(f'Step: {self.currentStep["key"]}')
        self.addvar()
        value = None
        try:
            extension = self.getExtension()
            value = self.handleReturnVariable(extension.handleStep(
                self.driver, self.currentStep, self.memory))
        except Exception as e:
            self.logError(e)
        if(value is not None and 'var' in self.currentStep):
            self.memory[self.currentStep['var']] = value

    def addvar(self):
        if(self.currentStep['key'] == 'var'):
            if(self.currentStep['name'] not in self.configMap):
                self.memory[self.currentStep['name']
                            ] = self.currentStep['value']
            else:
                self.logError(
                    f'Variable {self.currentStep["name"]} is a config variable')

    def loadConfig(self):
        with open('./config/steps.json') as configFile:
            return json.load(configFile)[0]

    def saveReport(self):
        with open(self.report, 'w') as reportFile:
            json.dump(self.reports, reportFile, indent=4)

    def log(self, message, color='white'):
        print(message)

    def logError(self, message):
        print(f"Error:\n\t{message}")
        if(self.driver):
            self.driver.close()
            self.driver.quit()
        sys.exit(1)

    def checkScenario(self):
        if(not 'scenario' in self.currentScenario['scenario']):
            return False, "Scenario not found in " + self.currentScenario['filename']
        if('name' not in self.currentScenario['scenario']['scenario']):
            return False, "Scenario name not found add name attribute to scenario tag"
        if(self.currentScenario['scenario']['scenario']['name'] == '' or
           self.currentScenario['scenario']['scenario']['name'].isspace()):
            return False, "Scenario name not found add name attribute to scenario tag"
        if('step' not in self.currentScenario['scenario']['scenario']):
            return False, "Scenario steps not found add step tag to scenario tag"
        return True, None

    def checkStep(self):
        if('key' not in self.currentStep):
            return False, "Step:  is not valid.\nNo key found."
        self.currentStep['key'] = self.currentStep['key'].lower()
        if(self.currentStep['key'] == '' or self.currentStep['key'].isspace()):
            return False, "Step:  is not valid.\nThe key is empty or contains only whitespace."
        return self.checkStepSyntax()

    def checkStepSyntax(self):
        if(self.currentStep['key'] not in self.config.keys()):
            return False, f"Step:  is not valid.\nThe key {self.currentStep['key']} does not exist."
        for param in self.config[self.currentStep['key']]['paramaters']:
            if(param not in self.currentStep):
                return False, f"Step:  is not valid.\nThe paramater {param} is missing.\nsyntax: {self.syntax(self.config[self.currentStep['key']]['paramaters'], self.currentStep['key'])}"
            if(self.currentStep[param] == '' or self.currentStep[param].isspace()):
                return False, f"Step:  is not valid.\nThe paramater {param} is empty or contains only whitespace."
        return True, None

    def syntax(self, syntax, tag):
        code = "<step key=\"" + tag + "\" "
        for key in syntax:
            code += f"{key}=\"value\" "
        code += "/>"
        return code

    def getExtension(self):
        extension = f"extensions.{self.config[self.currentStep['key']]['file']}"
        if(extension in self.extensions):
            return self.extensions[extension]
        self.extensions[extension] = importlib.import_module(extension)
        return self.extensions[extension]

    def loadStep(self, step=None):
        if(step is not None):
            self.currentStep = step
            format, error = self.checkStep()
            if(not format):
                self.addCurrentReportScenario()
                self.saveReport()
                self.logError(error)
        stepkeys: dict = self.currentStep
        # for each key in the step
        for key in stepkeys:
            stepkeys[key] = self.loadVariableFromMemory(stepkeys[key])
        return stepkeys

    def loadVariableFromMemory(self, variable):
        if(not(type(variable) is str)):
            return variable
        if(not self.usingConfig(variable)):
            self.returnType(variable.strip())
        if(">" not in variable):
            variableToLoad = variable.replace(
                " ", "").replace("[", "").replace("]", "")
            if(variableToLoad in self.memory):
                return self.memory[variableToLoad]
            else:
                return variable
        arguments = variable.replace('[', '').replace(
            ']', '').replace(' ', '').split('>')
        if(len(arguments) <= 1):
            return variable
        if (arguments[0] not in self.configMap):
            return variable
        current_arg = self.memory[arguments[0]]
        for arg in arguments[1:]:
            if(arg not in current_arg):
                self.logError(f"{arg} not found in {arguments[0]}")
            current_arg = current_arg[arg]

        return current_arg

    def returnType(self, value):
        if(value.isnumeric()):
            return int(value)
        if(value.lower() == 'true'):
            return True
        if(value.lower() == 'false'):
            return False
        if(re.match(r"[0-9]+\.?[0-9]*", value)):
            return float(value)
        return value

    def usingConfig(self, config):
        if re.match(config_syntax, config):
            return True
        return False

    def isVariable(self, variable):
        if(type(variable) is dict):
            if('type' in variable):
                if variable['type'] == 'var':
                    return True
        return False

    def handleReturnVariable(self, variable):
        if(self.isVariable(variable)):
            if(variable['name'].strip() != ''):
                self.memory[variable['name']] = variable['value'] if (
                    'value' in variable) else 0
        return variable
