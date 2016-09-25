from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

import Utilities as Utils


class RandomForest(object):
    """
        Random Forest Class.
    """
    def __init__(self):
        Utils.log('Initializing Random Forests.', Utils.class_log)
        self._clf = RandomForestClassifier()

    def train(self, features, labels):
        """
        A method for training the random forest Classifier on the provided \
        training set (features, labels).

        :param features: A list of 1d numpy arrays used as the feature vectors \
        for training.
        :param labels: A list of the appropriate labels for each training \
        feature vector.
        """
        self._clf.fit(features, labels)

    def predict_class(self, feature):
        """
        A method to predict the label for the provided feature vector. In this \
        context, a label is the predicted fantasy score of the player \
        associated with the feature vector.

        :param feature: a numpy 1d array that is used as the feature vector \
        for Random Forest classification.
        :return label: A label for the provided feature vector.
        """
        return self._clf.predict(feature)

    def __del__(self):
        Utils.log('Deleting Random Forests.', Utils.class_log)
        del self._clf


class Neighbors(object):
    """
       Nearest Neighbors class.
    """
    def __init__(self):
        Utils.log('Initializing K nearest neighbors.', Utils.class_log)
        self._clf = KNeighborsClassifier()

    def train(self, features, labels):
        """
        A method for training the nearest neighbor Classifier on the provided \
        training set (features, labels).

        :param features: A list of 1d numpy arrays used as the feature vectors \
        for training.
        :param labels: A list of the appropriate labels for each training \
        feature vector.
        """
        self._clf.fit(features, labels)

    def predict_class(self, feature):
        """
        A method to predict the label for the provided feature vector. In this \
        context, a label is the predicted fantasy score of the player \
        associated with the feature vector.

        :param feature: a numpy 1d array that is used as the feature vector \
        for Nearest Neighbor classification.
        :return label: A label for the provided feature vector.
        """
        return self._clf.predict(feature)

    def __del__(self):
        Utils.log('Deleting K nearest neighbors.', Utils.class_log)
        del self._clf
