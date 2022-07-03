import configparser
import importlib
import json
import os
import re
import time
from selenium import webdriver
from lib.timer import Timer

import lib.xmlCore as xml
from lib.args import handleArgs


config_syntax = r"\[[ ]*([a-zA-Z0-9_]+)[ ]*(>[ ]*[a-zA-Z0-9_]+[ ]*)*\]"


class EventHorizon:
    def __init__(self):
        """
        Initialize the EventHorizon class.
        Loading the config file and setting up the memory.
        """
        self.memory = {
            "[configs]": {},
            "[steps]": {},
            "[extensions]": {},
            "[report]": {
                "map": [],
                "data": []
            },
            "[options]": {
                "scenarios": "./scenarios",
                "browser": "chrome",
                "report": "./report.json",
                "remote": None,
                "maximize": False,
                "headless": False,
                "debug": False,
                "timeout": 10,
            },
            "[driver]": None,
            "[scenarios]": [],
            "[snippets]": [],
        }
        self.failed = False

    def loadArgs(self, file=None, jsonargs=None, dictargs=None):
        """
        Load the arguments from the config file or json string or dict or system argv.
        syntax:
            loadArgs(file=None, jsonargs=None, dictargs=None)
        """
        if file:
            if(os.path.exists(file)):
                """
                check if the file exists.
                and load the config file.
                """
                with open(file, 'r') as f:
                    args = json.load(f)
            else:
                self.logError("The config file does not exist.")
        elif jsonargs:
            """
            load the json string and convert it to dict.
            """
            args = json.loads(jsonargs)
        elif dictargs:
            """
            load the dict.
            """
            args = dictargs
        else:
            """
            load the system argv.
            """
            args = handleArgs()
        self.memory["[options]"]["scenarios"] = args["scenarios"]
        self.memory["[options]"]["browser"] = args["browser"] if args["browser"] else self.memory["[options]"]["browser"]
        self.memory["[options]"]["report"] = args["report"] if args["report"] else self.memory["[options]"]["report"]
        self.memory["[options]"]["remote"] = args["remote"] if args["remote"] else self.memory["[options]"]["remote"]
        self.memory["[options]"]["maximize"] = args["maximize"] if args["maximize"] else self.memory["[options]"]["maximize"]
        self.memory["[options]"]["headless"] = args["headless"] if args["headless"] else self.memory["[options]"]["headless"]

    def loadConfig(self, file=None):
        """
        Load the config file.
        syntax:
            LoadConfig(file=None)
        """
        if file:
            if(os.path.exists(file)):
                """
                check if the file exists.
                and load the config file.
                """
                with open(file, 'r') as f:
                    config = json.load(f)
                    self.memory["[steps]"] = config[0]
            else:
                self.logError("The config file does not exist.")
        else:
            if(not os.path.exists("./config/steps.json")):
                self.logError("The config file does not exist.")
            with open("./config/steps.json", 'r') as f:
                config = json.load(f)
                self.memory["[steps]"] = config[0]

    def loadScenarios(self, folder=None):
        """
        Load the scenarios from the folder.
        syntax:
            LoadScenarios(folder=None)
        """
        path = ""
        if folder:
            if(os.path.exists(folder)):
                """
                check if the folder exists.
                and load the scenarios.
                """
                path = folder
            else:
                self.logError("The scenarios folder does not exist.")
        else:
            path = self.memory["[options]"]["scenarios"]
            if(not os.path.exists(path)):
                self.logError("The scenarios folder does not exist.")

        files = [f for f in os.listdir(path) if f.lower().endswith('.xml')]
        for file in files:
            scenario = {
                "name": file,
            }
            file_path = os.path.join(path, file)
            xmlLoad = xml.loadXml(file_path)
            if("scenario" not in xmlLoad):
                self.logError("The scenario file is not valid.")
            scenario['body'] = xmlLoad['scenario']
            self.memory["[scenarios]"].append(scenario)

    def loadStepMap(self, scenarios=None):
        """
        Load the step map from the scenario.
        syntax:
            LoadStepMap(scenario=None)
        """
        localScenarios = self.memory["[scenarios]"]
        if(scenarios):
            localScenarios = scenarios
        for scenarioIndex, scenario in enumerate(localScenarios):
            stepsToMap = {"name": scenario["body"]["name"], "steps": []}
            for stepIndex, step in enumerate(scenario['body']['step']):
                stepsToMap["steps"].append({
                    "scenario": scenarioIndex,
                    "step": stepIndex,
                    "status": "failed",
                    "message": self.getDescription(step)
                })
            self.memory["[report]"]["map"].append(stepsToMap)

    def getDescription(self, step):
        """
        Get the description of the step.
        syntax:
            getDescription(step)
        """
        description = self.memory["[steps]"][step["key"].lower(
        )]["description"]
        if("[text]" in step):
            if(step["[text]"].strip()):
                description = step["[text]"]
        return description

    def checkStepsExist(self, steps=None):
        """
        Check if the steps exist.
        syntax:
            checkStepsExist(steps)
        """
        localScenarios = self.memory["[scenarios]"]
        if(steps):
            localSteps = steps
        for scenario in localScenarios:
            localSteps = scenario["body"]["step"]
            for step in localSteps:
                key = step['key']
                if(not key in self.memory["[steps]"]):
                    self.logError("The step '" + key + "' does not exist.")
                stepParamaters = self.memory["[steps]"][key]['paramaters']
                for paramater in stepParamaters:
                    if(not paramater in step):
                        self.logError(
                            "The step '" + key + "' does not have the paramater '" + paramater + "'.")

    def loadConfigScenario(self):
        scenario = self.currentScenario
        if('config' in scenario['body']):
            for config in scenario['body']['config']:
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
                    self.memory["[configs]"][path['name']] = config

    def loadSnippets(self):
        """
        Load the snippets from the folder.
        syntax:
            LoadSnippets()
        """
        snippets = {}
        for scenario in self.memory["[scenarios]"]:
            if("import" not in scenario["body"]):
                continue
            if("path" not in scenario["body"]["import"][0]):
                continue
            for path in scenario["body"]["import"][0]["path"]:
                if("name" not in path or "snippet" not in path):
                    self.logError("key 'name' or 'snippet' are missing.")
                if(not os.path.exists(path["snippet"])):
                    self.logError("The snippet file does not exist.")
                snippet = xml.loadXml(path["snippet"])
                if("snippet" not in snippet):
                    self.logError("The snippet tag does not exist.")
                snippet = snippet["snippet"]
                snippets[path["name"]] = snippet
        self.memory["[snippets]"] = snippets

    def loadDriver(self):
        """
        Load the driver.
        syntax:
            LoadDriver()
        """
        options = webdriver.ChromeOptions()
        if(self.memory["[options]"]["maximize"]):
            options.add_argument('--start-maximized')
        if(self.memory["[options]"]["headless"]):
            options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if self.memory["[options]"]["remote"] is None:
            if self.memory["[options]"]["browser"] == 'chrome':
                self.memory["[driver]"] = webdriver.Chrome(
                    options=options, executable_path="./drivers/chromedriver.exe")
            elif self.memory["[options]"]["browser"] == 'firefox':
                self.memory["[driver]"] = webdriver.Firefox()
            else:
                self.memory["[driver]"] = webdriver.Chrome(
                    options=options, executable_path="./drivers/chromedriver.exe")
        else:
            time.sleep(self.memory["[options]"]["timeout"])
            if(self.memory["[options]"]["browser"] == 'chrome'):
                self.memory["[driver]"] = webdriver.Remote(
                    command_executor=self.memory["[options]"]["remote"],
                    desired_capabilities=webdriver.DesiredCapabilities.CHROME)
            elif(self.memory["[options]"]["browser"] == 'firefox'):
                self.memory["[driver]"] = webdriver.Remote(
                    command_executor=self.memory["[options]"]["remote"],
                    desired_capabilities=webdriver.DesiredCapabilities.FIREFOX)
            else:
                self.memory["[driver]"] = webdriver.Remote(
                    command_executor=self.memory["[options]"]["remote"],
                    desired_capabilities=webdriver.DesiredCapabilities.CHROME)

    def run(self):
        """
        Run the scenarios.
        syntax:
            Run()
       """
        scenarios = self.memory["[scenarios]"]
        for index, scenario in enumerate(scenarios):
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
        """
        Run the scenario.
        syntax:
            RunScenario()
        """
        steps = self.currentScenario["body"]["step"]
        self.failed = False
        self.loadConfigScenario()
        for step in steps:
            self.currentStep = self.loadStep(step)
            if(not self.failed):
                if(self.currentStep["key"].lower().strip().startswith("snippet:")):
                    snippet = self.loadSnippet(
                        self.memory["[snippets]"][self.currentStep["key"].replace("snippet:", "").strip()])
                    self.runSnippet(
                        snippet
                    )
                format, error = self.checkStep()
                if(not format):
                    self.logError(error)
                timerStep = Timer()
                timerStep.start()
                try:
                    self.runStep()
                except Exception as e:
                    self.failed = True
                    timerStep.stop()
                    self.currentStepTime = timerStep.getTime()
                    self.addStepToReport("failed", str(e))
                    continue
                timerStep.stop()
                self.currentStepTime = timerStep.getTime()
            else:
                self.currentStepTime = 0
                self.addStepToReport("failed")
                continue
            self.addStepToReport()
        self.failed = False

    def loadSnippet(self, snippet):
        """
        Load the snippet.
        syntax:
            LoadSnippet(snippet)
        """
        currentStep = self.currentStep
        for step in snippet["step"]:
            for key in step:
                if(key == "step"):
                    continue
                for key2 in currentStep:
                    if(f"%%{key2}%%" in step[key]):
                        step[key] = currentStep[key2]
        return snippet

    def runSnippet(self, steps):
        """
        Run the scenario.
        syntax:
            RunScenario()
        """

        for step in steps["step"]:
            self.currentStep = self.loadStep(step)
            if(not self.failed):
                format, error = self.checkStep()
                if(not format):
                    self.logError(error)
                timerStep = Timer()
                timerStep.start()
                try:
                    self.runStep()
                except Exception as e:
                    self.failed = True
                    timerStep.stop()
                    self.currentStepTime = timerStep.getTime()
                    self.addStepToReport("failed", str(e))
                    continue
                timerStep.stop()
                self.currentStepTime = timerStep.getTime()
            else:
                self.currentStepTime = 0
                self.addStepToReport("failed")
                continue
            self.addStepToReport()
        self.failed = False

    def runStep(self):
        # self.currentStep = self.loadStep(step)
        self.log(f'Step: {self.currentStep["key"]}')
        self.addvar()
        value = None
        if(not self.failed):
            extension = self.getExtension()
            value = self.handleReturnVariable(extension.handleStep(
                self.memory["[driver]"], self.currentStep, self.memory))
        # except Exception as e:
        #     self.logError(e)
        if(value is not None and 'var' in self.currentStep):
            self.memory[self.currentStep['var']] = value

    def addvar(self):
        if(self.currentStep['key'] == 'var'):
            if(self.currentStep['name']):
                self.memory[self.currentStep['name']
                            ] = self.currentStep['value']
            else:
                self.logError(
                    f'Variable {self.currentStep["name"]} is a config variable')

    def addScenarioToReport(self):
        scenario = self.currentScenario
        data = {
            "keyword": "Feature",
            "uri": scenario['body']['name'],
            "name": scenario['body']['name'],
            "id": scenario['body']['name'],
            "line": 2,
            "description": "",
            "tags": [],
            "elements": [
                {
                    "keyword": "Scenario",
                    "id": scenario['body']['name'],
                    "name": scenario['body']['name'],
                    "line": 4,
                    "description": "",
                    "tags": [],
                    "type": "scenario",
                    "steps": []
                }
            ]
        }
        self.currentReportScenario = data

    def addStepToReport(self, status="passed", error=None):
        if(error is not None):
            self.logError(error)
        if self.failed:
            status = "failed"
        step = self.currentStep
        description = self.getDescription(step)
        data = {
            "keyword": "Step",
            "name": description,
            "line": 25,
            "match": {"location": ""},
            "result": {"status": status, "duration": self.currentStepTime}
        }
        self.currentReportScenario['elements'][0]['steps'].append(data)

    def addCurrentReportScenario(self):
        self.memory["[report]"]["data"].append(self.currentReportScenario)

    def checkScenario(self):
        if('name' not in self.currentScenario['body']):
            return False, "Scenario name not found add name attribute to scenario tag"
        if(self.currentScenario['body']['name'] == '' or
           self.currentScenario['body']['name'].isspace()):
            return False, "Scenario name not found add name attribute to scenario tag"
        if('step' not in self.currentScenario['body']):
            return False, "Scenario steps not found add step tag to scenario tag"
        return True, None

    def logError(self, error):
        if(not self.failed):
            self.failed = True
            print(f'Error: {error}')
        self.saveReport()
        return

    def checkStep(self):
        if('key' not in self.currentStep):
            return False, "Step:  is not valid.\nNo key found."
        self.currentStep['key'] = self.currentStep['key'].lower()
        if(self.currentStep['key'] == '' or self.currentStep['key'].isspace()):
            return False, "Step:  is not valid.\nThe key is empty or contains only whitespace."
        return self.checkStepSyntax()

    def checkStepSyntax(self):
        if(self.currentStep['key'] not in self.memory["[steps]"].keys()):
            return False, f"Step:  is not valid.\nThe key {self.currentStep['key']} does not exist."
        for param in self.memory["[steps]"][self.currentStep['key']]['paramaters']:
            if(param not in self.currentStep):
                stepParams = self.memory["[steps]"][self.currentStep['key']
                                                    ]['paramaters']
                return False, f"Step:  is not valid.\nThe paramater {param} is missing.\nsyntax: {self.syntax(stepParams, self.currentStep['key'])}"
            if(self.currentStep[param] == '' or self.currentStep[param].isspace()):
                return False, f"Step:  is not valid.\nThe paramater {param} is empty or contains only whitespace."
        return True, None

    def getExtension(self):
        extension = None
        key = self.currentStep["key"]
        extension = self.memory["[steps]"][self.currentStep['key']]['file']
        extension = f"extensions.{extension}"
        if(extension in self.memory["[extensions]"]):
            return self.memory["[extensions]"][extension]
        self.memory["[extensions]"][extension] = importlib.import_module(
            extension)
        return self.memory["[extensions]"][extension]

    def log(self, message, color='black'):
        print(f'{message}')
        return

    def saveReport(self):
        with open(self.memory["[options]"]["report"], 'w') as reportFile:
            json.dump(self.memory["[report]"]["data"], reportFile, indent=4)

    def syntax(self, syntax, tag):
        code = "<step key=\"" + tag + "\" "
        for key in syntax:
            code += f"{key}=\"value\" "
        code += "/>"
        return code

    def closeDriver(self):
        driver = self.memory["[driver]"]
        if(driver is not None):
            driver.close()
            driver.quit()
        return

    def loadStep(self, step=None):
        if(step is not None):
            self.currentStep = step
            format, error = self.checkStep()
            if(not format):
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
        current_arg = self.memory["[configs]"][arguments[0]]
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
