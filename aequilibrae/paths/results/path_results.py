import numpy as np


class PathResults:
    def __init__(self):
        """
        @type graph: Set of numpy arrays to store Computation results
        """
        self.predecessors = None
        self.connectors = None
        self.path_cost = None
        self.path = None
        self.path_nodes = None
        self.milepost = None
        self.reached_first = None

        self.links = -1
        self.nodes = -1
        self.zones = -1
        self.num_skims = -1
        self.__integer_type = None
        self.__float_type = None
        self.__graph_id__ = None

    def prepare(self, graph):
        self.__integer_type = graph.default_types('int')
        self.__float_type = graph.default_types('float')
        self.nodes = graph.num_nodes + 1
        self.zones = graph.centroids + 1
        self.links = graph.num_links + 1
        self.num_skims = graph.skims.shape[1]

        self.predecessors = np.zeros(self.nodes, dtype=self.__integer_type)
        self.connectors = np.zeros(self.nodes, dtype=self.__integer_type)
        self.reached_first = np.zeros(self.nodes, dtype=self.__integer_type)
        self.path_cost = np.zeros(self.nodes, self.__float_type)
        self.__graph_id__ = graph.__id__

    def reset(self):
        if self.predecessors is not None:
            self.predecessors.fill(-1)
            self.connectors.fill(-1)
            self.path_cost.fill(0)
            self.path = None
            self.path_nodes = None
            self.milepost = None

        else:
            print 'Exception: Path results object was not yet prepared/initialized'