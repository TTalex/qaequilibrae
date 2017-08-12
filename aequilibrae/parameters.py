import os
import yaml
import aequilibrae as ae

class Parameters:
    def __init__(self):
        self.path = os.path.dirname(ae.__file__)

        file = os.path.join(self.path, 'parameters.yml')
        with open(file, 'r') as yml:
            self.parameters = yaml.load(yml)

    def write_back(self):
        stream = open(self.path + '/parameters.yaml', 'w')
        yaml.dump(self.parameters, stream, default_flow_style=False)
        stream.close()