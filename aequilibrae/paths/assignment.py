"""
 -----------------------------------------------------------------------------------------------------------
 Package:    AequilibraE

 Name:       Traffic assignment
 Purpose:    Implement traffic assignment algorithms based on Cython's network loading procedures

 Original Author:  Pedro Camargo (c@margo.co)
 Contributors:
 Last edited by: Pedro Camrgo

 Website:    www.AequilibraE.com
 Repository:  https://github.com/AequilibraE/AequilibraE

 Created:    15/09/2013
 Updated:    2017-05-07
 Copyright:   (c) AequilibraE authors
 Licence:     See LICENSE.TXT
 -----------------------------------------------------------------------------------------------------------
 """


import sys
sys.dont_write_bytecode = True

try:
    import qgis
    from qgis.core import *
    from PyQt4.QtCore import SIGNAL
except:
    pass

import numpy as np
from multiprocessing.dummy import Pool as ThreadPool
import thread

from multi_threaded_aon import MultiThreadedAoN
no_binaries = False
try:
    from AoN import one_to_all, path_computation
except:
    no_binaries = True

def main():
    pass


def all_or_nothing(matrix, graph, results):
    aux_res = MultiThreadedAoN()
    aux_res.prepare(graph, results)

    # catch errors
    if results.__graph_id__ is None:
        raise ValueError('The results object was not prepared. Use results.prepare(graph)')
    elif results.__graph_id__ != graph.__id__:
        raise ValueError('The results object was prepared for a different graph')
    elif matrix.matrix_view is None:
        raise ValueError('Matrix was not prepared for assignment. '
                         'Please create a matrix_procedures view with all classes you want to assign')
    else:
        mat = matrix.matrix_view
        pool = ThreadPool(results.cores)
        all_threads = {'count': 0}
        report = []
        for O in range(matrix.zones):
            if np.sum(mat[O, :, :]) > 0:
                pool.apply_async(func_assig_thread, args=(O, matrix, graph, results, aux_res, all_threads, report))
        pool.close()
        pool.join()
    results.link_loads = np.sum(aux_res.temp_link_loads, axis=2)
    del aux_res
    return report


def func_assig_thread(O, matrix, g, res, aux_res, all_threads, report):
    if thread.get_ident() in all_threads:
        th = all_threads[thread.get_ident()]
    else:
        all_threads[thread.get_ident()] = all_threads['count']
        th = all_threads['count']
        all_threads['count'] += 1
    x = one_to_all(O, matrix, g, res, aux_res, th)
    if x != O:
        report.append(x)


if __name__ == '__main__':
    main()
