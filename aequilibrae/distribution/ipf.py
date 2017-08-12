"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       Iterative proportional fitting
 Purpose:    Implement Iterative proportional fitting

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camargo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    29/09/2016
 Updated:    11/08/2017
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 -----------------------------------------------------------------------------------------------------------
"""
import sys
sys.dont_write_bytecode = True

import numpy as np
import os
import yaml
from time import clock
from ..matrix import AequilibraeMatrix, AequilibraEData

class Ipf:
    def __init__(self, **kwargs):

        self.parameters = kwargs.get('parameters', self.get_parameters('ipf'))

        # Seed matrix
        self.matrix = kwargs.get('matrix', None)

        # row vector
        self.rows = kwargs.get('rows', None)
        self.row_field = kwargs.get('row_field', None)

        # Column vector
        self.columns = kwargs.get('columns', None)
        self.column_field = kwargs.get('column_field', None)

        self.output = None
        self.error = None
        self.__required_parameters=['convergence level', 'max iterations', 'balancing tolerance']
        self.error_free = True
        self.report = ['  #####    IPF computation    #####  ', '']
        self.gap = None

    def check_data(self):
        self.error = None
        self.check_parameters()

        # check data types
        if not isinstance(self.rows, AequilibraEData):
            raise TypeError('Row vector needs to be an instance of AequilibraEData')

        if not isinstance(self.columns, AequilibraEData):
            raise TypeError('Column vector needs to be an instance of AequilibraEData')

        if not isinstance(self.matrix, AequilibraeMatrix):
            raise TypeError('Seed matrix needs to be an instance of AequilibraEMatrix')

        # Check data dimensions
        if not np.array_equal(self.rows.index, self.columns.index):
            raise ValueError('Indices from row vector do not match those from column vector')

        if not np.array_equal(self.matrix.index, self.columns.index):
            raise ValueError('Indices from vectors do not match those from seed matrix')

        # Check if matrix was set for computation
        if self.matrix.matrix_view is None:
            raise ValueError('Matrix needs to be set for computation')
        else:
            if self.matrix.matrix_view.shape[2] > 1:
                raise ValueError("Matrix' computational view needs to be set for a single matrix core")

        if self.error is None:
            # check balancing:
            sum_rows = np.sum(self.rows.data[self.row_field])
            sum_cols = np.sum(self.columns.data[self.column_field])
            if abs(sum_rows - sum_cols) > self.parameters['balancing tolerance']:
                self.error = 'Vectors are not balanced'
            else:
                # guarantees that they are precisely balanced
                self.columns.data[self.column_field][:] = self.columns.data[self.column_field][:] * (
                    sum_rows / sum_cols)

        if self.error is not None:
            self.error_free = False

    def check_parameters(self):
        for i in self.__required_parameters:
            if i not in  self.parameters:
                self.error = 'Parameters error. It needs to be a dictionary with the following keys: '
                for t in self.__required_parameters:
                    self.error = self.error + t + ', '
                break

    def fit(self):
        t = clock()
        self.check_data()
        if self.error_free:
            max_iter = self.parameters['max iterations']
            conv_criteria = self.parameters['convergence level']

            self.output = self.matrix.copy()
            comput_core = self.output.view_names[0]
            rows = self.rows.data[self.row_field]
            columns = self.columns.data[self.column_field]
            tot_matrix = np.sum(self.output.matrix[comput_core][:, :])

            # Reporting
            self.report.append('Target convergence criteria: ' + str(conv_criteria))
            self.report.append('Maximum iterations: ' + str(max_iter))
            self.report.append('')
            self.report.append('Rows:' + str(self.rows.entries))
            self.report.append('Columns: ' + str(self.columns.entries))

            self.report.append('Total of seed matrix: ' + "{:28,.4f}".format(float(tot_matrix)))
            self.report.append('Total of target vectors: ' + "{:25,.4f}".format(float(rows.sum())))
            self.report.append('')
            self.report.append('Iteration,   Convergence')
            self.gap = conv_criteria + 1

            iter = 0
            while self.gap > conv_criteria and iter < max_iter:
                iter += 1
                # computes factors for zones
                marg_rows = self.tot_rows(self.output.matrix[comput_core][:,:])
                row_factor = self.factor(marg_rows, rows)
                # applies factor
                self.output.matrix[comput_core][:,:] = np.transpose(np.transpose(self.output.matrix[comput_core][:,:]) *
                                                                    np.transpose(row_factor))[:, :]

                # computes factors for columns
                marg_cols = self.tot_columns(self.output.matrix[comput_core][:,:])
                column_factor = self.factor(marg_cols, columns)

                # applies factor
                self.output.matrix[comput_core][:,:] = self.output.matrix[comput_core][:,:] * column_factor

                # increments iterarions and computes errors
                self.gap = max(abs(1 - np.min(row_factor)), abs(np.max(row_factor) - 1), abs(1 - np.min(column_factor)),
                            abs(np.max(column_factor) - 1))

                self.report.append(str(iter) + '   ,   ' + str("{:4,.10f}".format(float(np.sum(self.gap)))))

            self.report.append('')
            self.report.append('Running time: ' + str("{:4,.3f}".format(clock()-t)) + 's')
    def tot_rows(self, matrix):
        return np.sum(matrix, axis=1)

    def tot_columns(self, matrix):
        return np.sum(matrix, axis=0)

    def factor(self, marginals, targets):
        f = np.divide(targets, marginals)  # We compute the factors
        f[f == np.NINF] = 1  # And treat the errors, with the infinites first
        f = f + 1  # and the NaN second
        f = np.nan_to_num(f)  # The sequence of operations is just a resort to
        f[f == 0] = 2  # use at most numpy functions as possible instead of pure Python
        f = f - 1
        return f

    def get_parameters(self, model):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with open(path + '/parameters.yml', 'r') as yml:
            path = yaml.safe_load(yml)
        return path['distribution'][model]