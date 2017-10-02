"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       Gravity model calibration
 Purpose:    Implement a procedure to calibrate gravity models

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camargo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    22/10/2016
 Updated:    02/10/2017
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 -----------------------------------------------------------------------------------------------------------
"""

# The procedures implemented in this code are some of those suggested in
# Modelling Transport, 4th Edition
# Ortuzar and Willumsen, Wiley 2011

# The referred authors have no responsability over this work, of course

import sys, os
from time import clock, strftime, gmtime
from gravity_application import GravityApplication, SyntheticGravityModel
from ..matrix import AequilibraeMatrix, AequilibraEData
import numpy as np
import sys
import yaml
from ..parameters import Parameters

class GravityCalibration:
    """"
        where function is: 'EXPO' or 'POWER'. 'GAMMA' and 'FRICTION FACTORS' to be implemented at a later time
        parameters are: 'max trip length'
        """
    def __init__(self, **kwargs):

        self.__required_parameters = ['max trip length', 'max iterations', 'max error']
        self.parameters = kwargs.get('parameters', self.get_parameters())

        self.matrix = kwargs.get('matrix')
        self.impedance = kwargs.get('impedance')
        deterrence_function = str(kwargs.get('function', '')).upper()

        self.result_matrix = None
        self.rows = None
        self.columns = None
        self.gap = np.inf

        self.error = None
        self.gravity = None

        self.comput_core = None
        self.impedance_core = None

        self.itera = 0
        self.max_iter = None
        self.max_error = None
        self.gap = np.inf

        self.report = ['  #####    GRAVITY CALIBRATION    #####  ', '']
        self.report.append('Functional form: ' + deterrence_function)
        self.model = SyntheticGravityModel()
        if deterrence_function not in self.model.valid_functions:
            raise ValueError ('Function needs to be one of these: ' + ', '.join(self.model.valid_functions))
        else:
            self.model.function = deterrence_function

    def assemble_model(self, b1):
        # NEED TO SET PARAMETERS #
        if self.model.function == "EXPO":
            self.model.beta = float(b1)
        elif self.model.function == "POWER":
            self.model.alpha = float(b1)

    def calibrate(self):
        t = clock()
        # initialize auxiliary variables
        b0, b1, c0, c1 = None, None, None, None
        max_cost = self.parameters['max trip length']
        self.max_iter = self.parameters['max iterations']
        self.max_error = self.parameters['max error']


        # Check the inputs
        self.check_inputs()
        if self.model.function in ["EXPO", "POWER"]:
            # filtering for all costs over limit

            a = 1
            if max_cost > 0:
                a = (self.impedance.matrix[self.impedance_core][:, :] < max_cost).astype(int)

            #weighted average cost
            self.report.append('Iteration: 1')
            cstar = np.sum(self.impedance.matrix[self.impedance_core][:,:] * self.result_matrix.gravity[:, :]  * a) / \
                    np.sum(self.result_matrix.gravity[:, :]  * a)

            b0 = 1 / cstar

            self.assemble_model(b0)
            c0 = self.apply_gravity()
            for i in self.gravity.report:
                self.report.append('       ' + i)
            self.report.append('')
            self.report.append('')

            bm1 = b0
            bm = b0 * c0 / cstar

            self.report.append('Iteration: 2')
            self.assemble_model(bm)

            cm = self.apply_gravity()
            for i in self.gravity.report:
                self.report.append('       ' + i)
            self.report.append('Error: ' +  "{:.2E}".format(float(np.sum(abs((bm / bm1) - 1)))))
            self.report.append('')
            cm1 = c0

        # While the max iterations has not been reached and the error is still too large
        self.itera = 2
        while self.itera < self.max_iter and self.gap > self.max_error:
            self.report.append('Iteration: ' + str(self.itera + 1))
            aux = bm
            bm = ((cstar - cm1) * bm - (cstar - cm) * bm) / (cm - cm1)
            bm1 = aux
            cm1 = cm

            self.assemble_model(bm1)
            cm = self.apply_gravity()

            for i in self.gravity.report:
                self.report.append('       ' + i)
            self.report.append('Error: ' + "{:.2E}".format(float(np.sum(abs((bm / bm1) - 1)))))
            self.report.append('')

            # compute convergence criteria
            self.gap = abs((bm / bm1) - 1)
            self.itera += 1

        if self.itera == self.max_iter:
            self.report.append("DID NOT CONVERGE. Stopped in  " + str(self.itera) + "  with a global error of " + str(self.gap))
        else:
            self.report.append("Converged in " + str(self.itera) + "  iterations to a global error of " + str(self.gap))
        s = clock() - t
        m, s1 = divmod(s, 60)
        s -= m * 60
        h, m = divmod(m, 60)
        t =  "%d:%02d:%2.4f" % (h, m, s)

        self.report.append('Running time: ' + t)

    def check_inputs(self):
        if not isinstance(self.impedance, AequilibraeMatrix):
            raise TypeError('Impedance matrix needs to be an instance of AequilibraEMatrix')

        if not isinstance(self.matrix, AequilibraeMatrix):
            raise TypeError('Observed matrix needs to be an instance of AequilibraEMatrix')

        # Check data dimensions
        if not np.array_equal(self.impedance.index, self.impedance.index):
            raise ValueError('Indices from impedance matrix do not match those from seed matrix')

        # Check if matrices were set for computation
        mats = [(self.matrix, 'Observed matrix'), (self.impedance, 'Impedance matrix')]
        for matrix, title in mats:
            if matrix.matrix_view is None:
                raise ValueError(title + ' needs to be set for computation')
            else:
                if len(matrix.matrix_view.shape[:]) > 2:
                    raise ValueError(title + "' computational view needs to be set for a single matrix core")

            if np.sum(matrix.matrix_view.data) == 0:
                raise ValueError(title + 'has only zero values')
            if np.min(matrix.matrix_view.data) < 0:
                raise ValueError(title + 'has negative values')

        # Augment parameters if we happen to have only passed one
        default_parameters = self.get_parameters()
        for para in self.__required_parameters:
            if para not in self.parameters:
                self.parameters[para] = default_parameters[para]

        # Prepare the data for computation
        self.comput_core = self.matrix.view_names[0]

        self.result_matrix = self.matrix.copy(output_name='TEMP', cores=[self.comput_core], names=['gravity'])

        self.rows = AequilibraEData()
        self.rows.create_empty(entries=self.matrix.zones, field_names=['rows'], memory_mode=True)
        self.rows.index[:] = self.matrix.index[:]
        self.rows.rows[:] = self.matrix.rows()[:]

        self.columns = AequilibraEData()
        self.columns.create_empty(entries=self.matrix.zones, field_names=['columns'], memory_mode=True)
        self.columns.index[:] = self.matrix.index[:]
        self.columns.columns[:] = self.matrix.columns()[:]


        self.impedance_core = self.impedance.view_names[0]

    def apply_gravity(self):
        args = {'impedance': self.impedance,
                'rows': self.rows,
                'row_field': 'rows',
                'columns': self.columns,
                'column_field': 'columns',
                'model': self.model,
                'parameters': self.parameters}

        self.gravity = GravityApplication(**args)
        self.gravity.apply()
        self.result_matrix = self.gravity.output

        return np.sum(self.impedance.matrix[self.impedance_core][:,:] * self.result_matrix.gravity[:, :]) \
               / np.sum(self.result_matrix.gravity[:, :])

    def get_parameters(self):
        par = Parameters().parameters
        para = par['distribution']['ipf'].copy()
        para.update(par['distribution']['gravity'])
        return para
