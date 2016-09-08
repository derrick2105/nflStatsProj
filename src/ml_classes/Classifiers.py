from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

import Utilities as Utils


class RandomForest(object):
    def __init__(self):
        Utils.log('Initializing Random Forests.', Utils.class_log)
        self._clf = RandomForestClassifier()

    def train(self, features, labels):
        self._clf.fit(features, labels)

    def predict_class(self, feature):
        return self._clf.predict(feature)

    def __del__(self):
        Utils.log('Deleting Random Forests.', Utils.class_log)
        del self._clf


class Neighbors(object):
    def __init__(self):
        Utils.log('Initializing K nearest neighbors.', Utils.class_log)
        self._clf = KNeighborsClassifier()

    def train(self, features, labels):
        self._clf.fit(features, labels)

    def predict_class(self, feature):
        return self._clf.predict(feature)

    def __del__(self):
        Utils.log('Deleting K nearest neighbors.', Utils.class_log)
        del self._clf
