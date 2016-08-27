import Common
import DbMaintenance
# import numpy as np
import copy
from os import path


######
# TODO
#   1. Create store procedures to build and return a set of features for a
#       specified position as a list of tuples
#   2. Transform the tuples into a set of numpy array, probably a 1d array,
#      but possible an n-d array where n is the number of samples.
######

def import_features(import_file):
    feature_dictionary = {}

    with open(import_file, 'r') as f:
        for line in f.readlines():
            list_files = line.strip('\r\n').split(',')
            stat, value = list_files[0], float(list_files[1])
            feature_dictionary[stat] = value

    return feature_dictionary


######
# A wrapper class to extract features from the NFL data set. Replace and extend
# any of the provided features. I am assuming that we will need a feature
# vector for each fantasy position.
######
class ExtractFeatures:
    def __init__(self):
        self.db = DbMaintenance.DbMaintenance()
        self.db.import_db_config(Common.db_config)
        self.off_dict = {}
        self.def_dict = {}
        self.empty_off = {}
        self.empty_def = {}
        self.__populate_feature_dictionaries()

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

    def __populate_feature_dictionaries(self):
        self.off_dict = import_features(path.join(Common.point_breakdown_path,
                                        'offensive_draftday.csv'))
        self.def_dict = import_features(path.join(Common.point_breakdown_path,
                                        'defensive_draftday.csv'))

        empty_off_dict = copy.deepcopy(self.off_dict)
        empty_def_dict = copy.deepcopy(self.def_dict)
        for key in empty_off_dict.iterkeys():
            empty_off_dict[key] = 0.0
        for key in empty_def_dict.iterkeys():
            empty_def_dict[key] = 0.0

        self.empty_off = empty_off_dict
        self.empty_def = empty_def_dict

    def __extract_quarter_back(self):
        data = self.__get_data('QB')
        return data

    def __extract_wide_receiver(self):
        return self.__get_data('WR')

    def __extract_running_back(self):
        return self.__get_data('RB')

    def __extract_kicker(self):
        return self.__get_data('K')

    def __extract_defense(self):
        return self.__get_data('DEF')

    def __get_data(self, position, player_id=None, season_id=None):
        self.db.execute_stored_procedure('extract_statistics',
                                         args=[position, player_id, season_id])
        data = self.db.get_results(stored=True)
        self.db.close_connection()
        return data

    def __get_year_range(self):
        max_year, min_year = 0, 0
        statement1 = "select CAST(MAX(seasonYear) as UNSIGNED), " \
                     "CAST(MIN(seasonYear) as UNSIGNED) from Season;"

        if self.db.execute_statement(statement=statement1):
            max_year, min_year = self.db.get_results()[0]
        else:
            Common.log("Could not execute statement.", Common.populate_log)
        self.db.close_connection()
        return max_year, min_year

if __name__ == '__main__':
    feature_extractor = ExtractFeatures()

    for tup in feature_extractor.extract(Common.Position.quarterback):
        print tup[0], tup[1], tup[2], tup[3], float(tup[4])
