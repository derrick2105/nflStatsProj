import Common
import DbMaintenance
# import numpy as np
import copy
from os import path


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
        self.positions = {Common.Position.quarterback: 'QB',
                          Common.Position.running_back: 'RB',
                          Common.Position.kicker: 'K',
                          Common.Position.defense: 'DEF',
                          Common.Position.wide_receiver: 'WR'}
        self.off_dict_p = import_features(path.join(Common.point_breakdown_path,
                                        'offensive_draftday.csv'))
        self.def_dict_p = import_features(path.join(Common.point_breakdown_path,
                                        'defensive_draftday.csv'))

        self.off_dict_emp = {}
        self.def_dict_emp = {}
        self.__fill_empty_dicts()

    def __del__(self):
        del self.db

    def extract(self, position, current_season_id):
        Common.log('Entering extract method.', Common.extract_log)
        if position not in self.positions:
            Common.log('Error, invalid position.', Common.extract_log)
            return []

        Common.log('Pulling data from the database.', Common.extract_log)
        results = self.__get_data(self.positions[position],
                                  season_id=current_season_id)

        Common.log('Building feature vectors.', Common.extract_log)

        feature_list = []
        current_feature_dict = self.__get_fresh_feature_dict(position)
        current_player = results[0][0]

        print results[0]
        for line in results:
            if line[0] != current_player:
                feature_list.append((current_player, current_feature_dict))
                current_feature_dict = self.__get_fresh_feature_dict(position)
                current_player = line[0]

            if str(line[3]) in current_feature_dict:
                if position == Common.Position.defense:
                    current_feature_dict[str(line[3])] = float(line[4]) * \
                                        self.def_dict_p[str(line[3])]
                else:
                    current_feature_dict[str(line[3])] = float(line[4]) * \
                                        self.off_dict_p[str(line[3])]

        # print current_player
        Common.log('Exiting extract method.', Common.extract_log)
        return feature_list

    def __get_fresh_feature_dict(self, position):
        if position == Common.Position.defense:
            return_dict = copy.deepcopy(self.def_dict_emp)
        else:
            return_dict = copy.deepcopy(self.off_dict_emp)

        return return_dict

    def __fill_empty_dicts(self):
        self.off_dict_emp = copy.deepcopy(self.off_dict_p)
        self.def_dict_emp = copy.deepcopy(self.off_dict_p)

        for k in self.off_dict_emp:
            self.off_dict_emp[k] = 0.0

        for k in self.def_dict_emp:
            self.def_dict_emp[k] = 0.0

    def __get_data(self, position, player_id=None, season_id=None):
        self.db.execute_stored_procedure('extract_statistics',
                                         args=[position, season_id, player_id])

        data = self.db.get_results(stored=True)
        self.db.close_connection()
        return data

if __name__ == '__main__':
    feature_extractor = ExtractFeatures()

    for t in feature_extractor.extract(Common.Position.quarterback, 101):
        print t[0], t[1]
