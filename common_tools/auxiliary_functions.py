"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       AequilibraE auxiliary Functions
 Purpose:

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camargo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    2014-03-19
 Updated:    26/02/2017
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 ------------------auxiliary_functions-----------------------------------------------------------------------------------------
 """

import qgis
from qgis.core import QgsMapLayerRegistry
import math
import os
import yaml
import tempfile
from time import localtime, strftime

def main():
    pass

def user_message(message, level):
    if level == "WARNING":
        level = 1
    if level == "ERROR":
        level = 3

    qgis.utils.iface.messageBar().pushMessage(message, '', level=level)

# Just a shorthand function to return the current standard path
def standard_path():
    return get_parameter_chain(['system', 'default_directory'])

def tempPath():
    tmp_path = get_parameter_chain(['system', 'temp directory'])
    if os.path.isdir(tmp_path):
        return tmp_path
    else:
        return tempfile.gettempdir()

# Returns the parameter for a given hierarchy of groups in a dictionary of dictionaries (recovered from a yml)
def get_parameter_chain(chain):
    head = chain.pop(0)
    g = get_parameters_group(head)
    while len(chain) > 0:
        head = chain.pop(0)
        if head in g:
            g = g[head]
        else:
            chain = []
            g = {}
    return g

# Recovers a group of parameters (or the entire yml) as a dictionary of dictionaries
def get_parameters_group(group=None):
    path = os.path.dirname(os.path.dirname(__file__))  + "/aequilibrae/"
    with open(path + 'parameters.yml', 'r') as yml:
        path = yaml.safe_load(yml)
    if group is None:
        return path
    if group in path:
        return path[group]
    else:
        return {}

def get_vector_layer_by_name(layer_name):
    layer = QgsMapLayerRegistry.instance().mapLayersByName(layer_name)
    if not layer:
        return None
    else:
        return layer[0]

# Haversine formula here:
# http://gis.stackexchange.com/questions/44064/how-to-calculate-distances-in-a-point-sequence/56589#56589
def haversine(lon1, lat1, lon2, lat2):
    # Calculate the great circle distance between two points
    # on the earth (specified in decimal degrees)

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    d_lon = lon2 - lon1
    d_lat = lat2 - lat1
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    meters = 6378137 * c
    return meters


def logger(message):
    debug_file = tempfile.gettempdir() + '/aequilibrae.log'
    if not os.path.exists(debug_file):
        o = open(debug_file, 'w')
    else:
        o = open(debug_file, 'a')
    if type(message) in [list, tuple, dict]:
        message = str(message)
    print >>o, message
    o.flush()
    o.close()


def reporter(message, tabs=0):
    t = strftime("%Y-%m-%d %H:%M:%S", localtime())
    return ' ' * tabs + t + ' - ' +str(message)


if __name__ == '__main__':
    main()
