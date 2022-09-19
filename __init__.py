# This portion of the script initializes the plugin, making it known to QGIS.
import sys
from os.path import abspath, join, dirname

sys.path.insert(0, abspath(join(dirname(__file__), "aequilibrae")))


def classFactory(iface):
    from .aequilibrae_menu import AequilibraEMenu

    return AequilibraEMenu(iface)
