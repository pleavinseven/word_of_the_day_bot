import json

config_file = "./config/config.json"
config_dict = {}


def load_config():
    global config_dict

    with open(config_file, "r") as file:
        config_dict = json.load(file)


load_config()
