"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       Report dialog
 Purpose:    Dialog for showing the report from algorithm runs

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camargo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    2014-03-19
 Updated:    30/09/2016
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 -----------------------------------------------------------------------------------------------------------
 """

from qgis.core import *
from PyQt4 import QtGui
from PyQt4.QtGui import *

import sys
import os
from auxiliary_functions import standard_path

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/forms/")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/aequilibrae/")

from ui_report import Ui_report

class ReportDialog(QtGui.QDialog, Ui_report):
    def __init__(self, iface, reporting):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.path = standard_path()
        self.reporting = reporting
        for t in reporting:
            self.all_data.append(t)

        self.but_save_log.clicked.connect(self.save_log)

    def save_log(self):
        file_types = "Text files(*.txt)"
        new_name = QFileDialog.getSaveFileName(None, 'Save log', self.path, file_types)
        if len(new_name)>0:
            outp = open(new_name, 'w')
            for t in self.reporting:
                print >> outp, t
            outp.flush()
            outp.close()
            self.exit_procedure()

    def exit_procedure(self):
        self.close()
