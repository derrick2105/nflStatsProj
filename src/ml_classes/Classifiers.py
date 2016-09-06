from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

import src.Utilities as Utils


class RandomForest(object):
    def __init__(self):
        Utils.log('Initializing Random Forests.', Utils.class_log)
        self.clf = RandomForestClassifier()

    def __del__(self):
        Utils.log('Deleting Random Forests.', Utils.class_log)
        del self.clf


class Neighbors(object):
    def __init__(self):
        Utils.log('Initializing K nearest neighbors.', Utils.class_log)
        self.clf = KNeighborsClassifier()

    def __del__(self):
        Utils.log('Deleting K nearest neighbors.', Utils.class_log)
        del self.clf
