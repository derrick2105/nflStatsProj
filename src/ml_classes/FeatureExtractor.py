import src.Utilities
import copy
from os import path

positions = src.Utilities.Positions.get_positions()


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
    def __init__(self, off_scoring_file_name='offensive_draftday.csv',
                 def_scoring_file_name='defensive_draftday.csv'):

        # offensive and defensive point breakdowns for each stat
        self.off_dict_p = import_feat(path.join(
            src.Utilities.point_breakdown_path, off_scoring_file_name))
        self.def_dict_p = import_feat(path.join(
            src.Utilities.point_breakdown_path, def_scoring_file_name))

        # empty weekly stats dicts
        self.off_dict_emp = {}
        self.def_dict_emp = {}
        self.__fill_empty_dicts()

        # empty weekly feature
        # [points, opponent, location, turf]
        self.empty_feature_vector = []

    def extract_feature(self, position, current_season_id):
        global positions
        src.Utilities.log('Entering extract method.', src.Utilities.extract_log)

        # select game_info statement
        statement = "select s.locationId, s.turf, g.homeTeam, g.awayTeam from "\
                    "TeamLocations s, Games g where s.teamId = g.homeTeam " \
                    "and g.seasonId = %s;"

        if not statement:
            return []

        if position not in positions:
            src.Utilities.log('Error, invalid position.',
                              src.Utilities.extract_log)
            return []

        src.Utilities.log('Pulling data from the database.',
                          src.Utilities.extract_log)

        results = self.__get_data('extract_statistics', [positions[position],
                                                         current_season_id,
                                                         None])

        res = self.__get_data('extract_game_info',
                              [current_season_id,
                               positions[position]])

        if not results or not res:
            src.Utilities.log('Empty result set.',
                              src.Utilities.extract_log)

        player_game_info = {}
        for item in res:
            player_game_info[item[0]] = (item[1], item[2], item[3])
        src.Utilities.log('Building feature vectors.',
                          src.Utilities.extract_log)

        feature_list = []
        point_sum = 0
        current_feature_dict = self.__get_fresh_feature_dict(position)
        current_player = results[0][0]

        for line in results:
            if line[0] != current_player:
                if current_player not in player_game_info:
                    current_player = line[0]
                    continue

                feature_vector = [round(point_sum, 2),
                                  player_game_info[current_player][0],
                                  player_game_info[current_player][1],
                                  player_game_info[current_player][2]]
                feature_list.append((current_player, feature_vector))

                point_sum = 0
                current_feature_dict = self.__get_fresh_feature_dict(position)
                current_player = line[0]

            if str(line[3]) in current_feature_dict:
                if position == src.Utilities.Positions.defense:
                    point_sum += float(line[4]) * self.def_dict_p[str(line[3])]

                else:
                    point_sum += float(line[4]) * self.off_dict_p[str(line[3])]

        if current_player in player_game_info:

            feature_vector = [round(point_sum, 2),
                              player_game_info[current_player][0],
                              player_game_info[current_player][1],
                              player_game_info[current_player][2]]
            feature_list.append((current_player, feature_vector))

        src.Utilities.log('Exiting extract method.', src.Utilities.extract_log)
        return feature_list

    def __get_fresh_feature_dict(self, position):
        if position == src.Utilities.Positions.defense:
            return_dict = self.def_dict_emp
        else:
            return_dict = self.off_dict_emp

        return return_dict

    def __fill_empty_dicts(self):
        self.off_dict_emp = copy.deepcopy(self.off_dict_p)
        self.def_dict_emp = copy.deepcopy(self.def_dict_p)

        for k in self.off_dict_emp:
            self.off_dict_emp[k] = 0.0

        for k in self.def_dict_emp:
            self.def_dict_emp[k] = 0.0

    @staticmethod
    def __get_data(procedure, args):
        return src.Utilities.execute_procedure(procedure,
                                               args,
                                               src.Utilities.extract_log)
