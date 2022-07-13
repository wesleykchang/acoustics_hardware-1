import json

with open("picoscope/settings.json") as f:
    settings = json.load(f)
sigGenBuiltIn = settings["sigGenBuiltIn"]
print(sigGenBuiltIn)

