import yaml
with open("./utils/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)