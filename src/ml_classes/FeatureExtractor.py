import src.Utilities
# import numpy as np
import copy
from os import path

positions = {src.Utilities.Position.quarterback: 'QB',
             src.Utilities.Position.running_back: 'RB',
             src.Utilities.Position.kicker: 'K',
             src.Utilities.Position.defense: 'DEF',
             src.Utilities.Position.wide_receiver: 'WR'}


def import_feat(import_file):
    feature_dictionary = {}

    with open(import_file, 'r') as f:
        for line in f.readlines():
            list_files = line.strip('\r\n').split(',')
            stat, value = list_files[0], float(list_files[1])
            feature_dictionary[stat] = value

    return feature_dictionary


######
# A wrapper class to extract features from the NFL data set. Replace and extend
# any of the provided features.
######
class FeatureExtractor:
    def __init__(self):
        self.off_dict_p = import_feat(path.join(
            src.Utilities.point_breakdown_path,
                                      'offensive_draftday.csv'))
        self.def_dict_p = import_feat(path.join(
            src.Utilities.point_breakdown_path,
                                      'defensive_draftday.csv'))

        self.off_dict_emp = {}
        self.def_dict_emp = {}
        self.__fill_empty_dicts()

    def __del__(self):
        pass

    def extract(self, position, current_season_id):
        global positions
        src.Utilities.log('Entering extract method.', src.Utilities.extract_log)

        if position not in positions:
            src.Utilities.log('Error, invalid position.',
                              src.Utilities.extract_log)
            return []

        src.Utilities.log('Pulling data from the database.',
                          src.Utilities.extract_log)

        results = self.__get_data(positions[position],
                                  season_id=current_season_id)

        if not results:
            src.Utilities.log('Empty result set.',
                              src.Utilities.extract_log)

        src.Utilities.log('Building feature vectors.',
                          src.Utilities.extract_log)

        feature_list = []
        current_feature_dict = self.__get_fresh_feature_dict(position)
        current_player = results[0][0]

        for line in results:
            if line[0] != current_player:
                feature_list.append((current_player, current_feature_dict))
                current_feature_dict = self.__get_fresh_feature_dict(position)
                current_player = line[0]

            if str(line[3]) in current_feature_dict:
                if position == src.Utilities.Position.defense:
                    current_feature_dict[str(line[3])] = float(line[4]) * \
                                        self.def_dict_p[str(line[3])]
                else:
                    current_feature_dict[str(line[3])] = float(line[4]) * \
                                        self.off_dict_p[str(line[3])]

        # print current_player
        src.Utilities.log('Exiting extract method.', src.Utilities.extract_log)
        return feature_list

    def __get_fresh_feature_dict(self, position):
        if position == src.Utilities.Position.defense:
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

    @staticmethod
    def __get_data(position, player_id=None, season_id=None):
        return src.Utilities.execute_procedure('extract_statistics',
                                               [position, season_id, player_id],
                                               src.Utilities.extract_log)

if __name__ == '__main__':
    feature_extractor = FeatureExtractor()

    for t in feature_extractor.extract(src.Utilities.Position.quarterback, 101):
        print t[0], t[1]
