import yaml
import numpy as np

def load_conf_yaml(yamlfile):
    with open(yamlfile) as yml:
        config = yaml.safe_load(yml)
        config["init_board"] = np.array(config["init_board"])
        config["n_players"] = len(config["player_colors"])

    return config
if __name__ == "__main__":
    from pprint import pprint
    pprint(load_conf_yaml("../config_default.yaml"))
