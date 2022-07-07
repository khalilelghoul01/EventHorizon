import json
import os

from lib.EventHorizon import EventHorizon


os.chdir(os.path.dirname(os.path.abspath(__file__)))

launcher = EventHorizon()
try:
    # launcher.loadArgs()
    # launcher.loadConfig()
    # launcher.loadScenarios("./scenario")
    # launcher.loadStepMap()
    # launcher.loadSnippets()
    # launcher.loadDriver()
    # launcher.run()
    # launcher.closeDriver()
    # launcher.saveReport()
    launcher.loadArgs().loadConfig().loadScenarios(
        "./scenario").loadStepMap().loadSnippets().loadDriver().run().closeDriver().saveReport()
except Exception as e:
    launcher.closeDriver().saveReport()
    print(e)
    exit(1)

# launcher.loadArgs()
# launcher.loadConfig()
# launcher.loadScenarios("./scenario")
# launcher.loadStepMap()
# launcher.loadSnippets()
# launcher.loadDriver()
# launcher.run()
# launcher.closeDriver()
# launcher.saveReport()
