import src.Utilities as Utils
import src.ml_classes.FeatureExtractor
import src.ml_classes.Classifiers
import sys

GAMES_BACK = 6

if len(sys.argv) > 1:
    import_class = sys.argv[1].lower()
else:
    import_class = 'randomforest'

Utils.log('Building classifiers', Utils.driver_log)

if import_class == 'randomforest':
    clf = src.ml_classes.Classifiers.RandomForest()

elif import_class == 'kneighbors':
    clf = src.ml_classes.Classifiers.KNeighborsClassifier()


Utils.log('Extracting features.', Utils.driver_log)
extractor = src.ml_classes.FeatureExtractor.FeatureExtractor()


current_season_id = (Utils.get_current_season() - Utils.starting_year)*17 + \
                    Utils.current_week

position_x_y_dicts = {}

# will play around to make it better in the next few weeks

for season_id in xrange(current_season_id - GAMES_BACK, current_season_id):
    print 'extracting stats for season_id: ', season_id
    for position in Utils.Positions.get_positions():
        if position not in position_x_y_dicts:
            position_x_y_dicts[position] = {}
        feature_list = extractor.extract_feature(position, season_id)
        for item in feature_list:
            player, x, y = item[0], item[1][1:], item[1][0]
            if player not in position_x_y_dicts[position]:
                position_x_y_dicts[position][player] = ([], [])

            position_x_y_dicts[position][player][0].append(x)
            position_x_y_dicts[position][player][1].append(y)

for key, item in position_x_y_dicts.iteritems():
    for l in item:
        while len(position_x_y_dicts[key][l][0]) < GAMES_BACK:
            position_x_y_dicts[key][l][0].append([0, 0, 0])
            position_x_y_dicts[key][l][1].append(0.0)

for key, item in position_x_y_dicts.iteritems():
    print key, item

Utils.log('Finished extracting features.', Utils.driver_log)
Utils.log('labeling players', Utils.driver_log)