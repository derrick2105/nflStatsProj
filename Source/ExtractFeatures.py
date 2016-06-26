import Common
import DbMaintenance


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
        pass
