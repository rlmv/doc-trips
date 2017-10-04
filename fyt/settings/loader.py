import os

import yaml


class EnvLoader:
    """
    Settings loader which first tries to pull values from the environment,
    then falls back to a yaml configuration file for local development.
    """
    def __init__(self, config_file=None):
        if config_file and os.path.isfile(config_file):
            with open(config_file) as f:
                values = yaml.load(f.read())
        else:
            values = {}

        self.loaded = values

    def get(self, name, default=''):
        if name in os.environ:
            return os.environ[name]
        return self.loaded.get(name, default)
