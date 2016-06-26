import Common
import DbMaintenance
import numpy as np


######
# TODO
#   1. Create store procedures to build and return a set of features for a
#       specified position as a list of tuples
#   2. Transform the tuples into a set of numpy array, probably a 1d array,
#      but possible an n-d array where n is the number of samples.
######

######
# A wrapper class to extract features from the NFL data set. Replace and extend
# any of the provided features. I am assuming that we will need a feature
# vector for each fantasy position.
######
class ExtractFeatures:
    def __init__(self):
        self.db = DbMaintenance.DbMaintenance()
        self.db.import_db_config(Common.db_config)

    def __del__(self):
        del self.db

    def extract(self, position):
        results = None
        if position == Common.Position.quarterback:
            results = self.__extract_quarter_back()
        elif position == Common.Position.running_back:
            results = self.__extract_running_back()
        elif position == Common.Position.wide_receiver:
            results = self.__extract_wide_receiver()
        elif position == Common.Position.kicker:
            results = self.__extract_kicker()
        elif position == Common.Position.defense:
            results = self.__extract_defense()

        return results

    def __extract_quarter_back(self):
        self.__get_data()
        np.random.random(1)
        return 1

    def __extract_wide_receiver(self):
        self.__get_data()
        return 1

    def __extract_running_back(self):
        self.__get_data()
        return 1

    def __extract_kicker(self):
        self.__get_data()
        return 1

    def __extract_defense(self):
        self.__get_data()
        return 1

    def __get_data(self):
        pass
