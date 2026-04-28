import json

def load_settings():
    with open("settings.json") as f:
        return json.load(f)

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)