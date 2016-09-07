#!/usr/bin/python
from os import listdir, path

import Utilities
from wrapper_classes.DbMaintenance import DbMaintenance
from wrapper_classes.StatisticsProvider import NFLStatsProvider as Provider


####
# TODO:
#   1. Refactor populate_player_stats to pull out individual weekly stats pulls
#   2. Add a weekly player stats update
#
#   Issue where LP Field is used instead of Nissan Stadium
#   Current implementation will improperly assign locationId for
#   international games
####

class PopulateNFLDB:
    def __init__(self):
        self.DB = DbMaintenance()
        self.provider = Provider()
        self.DB.import_db_config(Utilities.db_config)

    def __del__(self):
        del self.DB
        del self.provider

    def populate_all(self):
        # Add all of the non player specific information.
        self.populate_seasons()
        self.populate_teams()
        self.populate_games_from_data(Utilities.schedule_data_path)
        self.populate_new_season_games()
        self.populate_stats()
        self.populate_weather()

        # Add each player, their statistics, and their injury report.
        # Currently only adds the latest injury report.
        self.populate_players()
        self.populate_player_stats()
        self.populate_injury_report()

    def populate_players(self):
        statement1 = "insert IGNORE into Players (playerId, firstName, " \
                     "lastName, position) values (%s, %s, %s, %s);"

        statement2 = "insert replace into PlayerTeam(playerId, teamId)" \
                     " values (%s, %s);"

        for season in range(2010, 2016):
            message = "Downloading players from " + str(season)
            Utilities.log(message, Utilities.populate_log)

            insert_tuples1 = []
            insert_tuples2 = []

            for week in range(1, 18):
                try:
                    results = self.provider.get_data(
                        Utilities.StatType.playerInfo, week, season)[
                        'players']

                    for value in results:
                        tup = (int(value['id']), str(value['firstName']),
                               str(value['lastName']), str(value['position']))

                        if tup not in insert_tuples1:
                            insert_tuples1.append(tup)
                        if str(value['teamAbbr']) != '':
                            tup2 = (int(value['id']), str(value['teamAbbr']))
                            if tup2 not in insert_tuples2:
                                insert_tuples2.append(tup2)

                except TypeError or KeyError, e:
                    Utilities.log_exception(e, Utilities.populate_log)
                    return False

            message = "Inserting values for season: " + str(season) + \
                      " into the database."

            Utilities.log(message, Utilities.populate_log)
            if not Utilities.populate_db(statement1, Utilities.populate_log,
                                         insert_tuples1) \
               or not Utilities.populate_db(statement2, Utilities.populate_log,
                                            insert_tuples2):
                Utilities.log("Problem executing statement in the database."
                              " Aborting.", Utilities.populate_log)

                return False
        return True

    def populate_stats(self):
        result = self.provider.get_data(
            Utilities.StatType.statistics)['stats']

        statement = "INSERT IGNORE into Statistics (statID, stat_name) values" \
                    " (%s, %s);"

        insert_tuples = []
        try:
            for value in result:
                insert_tuples.append((int(value['id']), str(value['name'])))

            if not Utilities.populate_db(statement, Utilities.populate_log,
                                         insert_tuples):
                Utilities.log("Problem executing statement in the database."
                              " Aborting.", Utilities.populate_log)

                return False

        except TypeError or KeyError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False

        return True

    def populate_new_season_games(self):
        get_statement1 = "Select MAX(seasonId) from Season;"
        get_statement2 = "Select MAX(seasonId) from Games;"
        put_statement1 = "Insert Ignore into Games (seasonID, homeTeam, " \
                         "awayTeam, gameTime) values (%s, %s, %s, %s);"

        put_statement2 = "Insert Ignore into ByeWeeks (seasonId, teamId) " \
                         "values (%s, %s);"

        max_season_id = Utilities.pull_from_db(get_statement1,
                                               Utilities.populate_log)[0][0]

        games_max_id = Utilities.pull_from_db(get_statement2,
                                              Utilities.populate_log)[0][0]

        if max_season_id != games_max_id:
            # Possibly refactor this line. It can cause the db to become
            # inconsistent
            games_max_id = (Utilities.get_current_season() -
                            Utilities.starting_year) * 17

            try:
                results1 = self.provider.get_data(
                    data_type=Utilities.StatType.games)['Schedule']

                insert_tuples1 = []

                for result in results1:
                    if result['homeTeam'] == 'JAC':
                        result['homeTeam'] = 'JAX'
                    if result['awayTeam'] == 'JAC':
                        result['awayTeam'] = 'JAX'
                    tup = (games_max_id + int(result['gameWeek']),
                           str(result['homeTeam']), str(result['awayTeam']),
                           str(Utilities.convert_to_24(
                               result['gameTimeET'])))
                    insert_tuples1.append(tup)

                results2 = self.provider.get_data(
                    data_type=Utilities.StatType.byes)

                insert_tuples2 = []
                for week in results2.iteritems():
                    for team_dict in week[1]:
                        tup = (games_max_id + int(team_dict['byeWeek']),
                               str(team_dict['team']))
                        print tup
                        insert_tuples2.append(tup)

                print "Inserting into the Database"
                if not Utilities.populate_db(put_statement1,
                                             Utilities.populate_log,
                                             insert_tuples1):
                    Utilities.log("Problem executing statement in the "
                                  "database...Aborting.",
                                  Utilities.populate_log)

                    return False

                if not Utilities.populate_db(put_statement2,
                                             Utilities.populate_log,
                                             insert_tuples2):
                    Utilities.log("Problem executing statement in the "
                                  "database...Aborting.",
                                  Utilities.populate_log)

                    return False

            except TypeError or KeyError, e:
                Utilities.log_exception(e, Utilities.populate_log)
                return False

        return True

    @staticmethod
    def populate_games_from_data(data_path=Utilities.schedule_data_path):
        start_year = Utilities.starting_year
        put_statement1 = "Insert ignore into Games (seasonId, homeTeam, " \
                         "awayTeam) values (%s, %s, %s);"

        put_statement2 = "Insert Ignore into ByeWeeks (seasonId, teamId) " \
                         "values (%s, %s);"

        try:
            # Assuming data_files have the naming convention <year>_sched.csv
            data_files = [file_name for file_name in sorted(listdir(
                data_path)) if path.isfile(path.join(data_path,
                                                     file_name))]

        except OSError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False

        insert_tuples1 = []
        insert_tuples2 = []
        for file_name in data_files:
            try:
                offset = int(file_name[0:4]) - start_year
            except ValueError, e:
                Utilities.log_exception(e, Utilities.populate_log)
                return False

            file_name = path.join(data_path, file_name)
            with open(file_name) as f:
                for line in f:
                    team_schedule = line.strip('\r\n').split(',')
                    try:
                        for index in xrange(1, len(team_schedule)):
                            season_id = offset * 17 + index

                            if team_schedule[index].upper() == "BYE":
                                insert_tuples2.append((season_id,
                                                       team_schedule[0]))
                                continue

                            if team_schedule[index][0] == '@':
                                tup = (season_id, team_schedule[index][1:],
                                       team_schedule[0])
                            else:
                                tup = (season_id, team_schedule[0],
                                       team_schedule[index])

                            if tup not in insert_tuples1:
                                insert_tuples1.append(tup)

                    except IndexError, e:
                        Utilities.log_exception(e, Utilities.populate_log)
                        return False

        print "inserting games into the Database."
        if not Utilities.populate_db(put_statement1, Utilities.populate_log,
                                     insert_tuples1):
            Utilities.log("Couldn't insert games int the database.",
                          Utilities.populate_log)

            return False
        if not Utilities.populate_db(put_statement2, Utilities.populate_log,
                                     insert_tuples2):
            Utilities.log("Couldn't insert games int the database.",
                          Utilities.populate_log)

            return False
        return True

    def populate_new_season(self, year=None):
        if not year:
            Utilities.update_season(
                Utilities.get_current_season() + 1)
        else:
            Utilities.update_season(year)
        Utilities.update_week(1)
        return self.populate_seasons(year, year + 1)

    def populate_injury_report(self):
        get_statement = 'select playerId from Players;'
        insert_statement = 'REPLACE into InjuryReport (playerId, ' \
                           'injurySeverity) values (%s, %s);'

        insert_tuples = []
        print "Retrieving injury reports."
        count = 0
        id_tuples = Utilities.pull_from_db(get_statement,
                                           Utilities.populate_log)
        tuple_count = float(len(id_tuples))
        for id_tup in id_tuples:
            count += 1
            if count % 100 == 0:
                print "Percentage of reports gathered so far: ", \
                    round(count * 100 / tuple_count, 2)

            try:
                stats = self.provider.get_data(
                    data_type=Utilities.StatType.injury,
                    player_id=id_tup[0])

                insert_tuples.append((id_tup[0], str(stats['players'][0]
                                                     ['injuryGameStatus'])))
            except TypeError or KeyError, e:
                Utilities.log_exception(e, Utilities.populate_log)
                return False

        message = "Inserting player Injury Statuses into the database."

        print message
        Utilities.log(message, Utilities.populate_log)
        if not Utilities.populate_db(insert_statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log("Problem executing statement in the database. "
                          "Aborting.", Utilities.populate_log)

            return False
        return True

    def populate_player_stats(self):
        season_id = 1
        statement = "Insert IGNORE into PlayerStats (playerId, statId, " \
                    "Seasonid, statValue) values (%s, %s, %s, %s);"

        for year in range(2010, 2016):
            message = "Downloading player stats from " + str(year)
            print message
            Utilities.log(message, Utilities.populate_log)
            insert_tuples = []
            for week in range(1, 18):
                try:
                    results = self.provider.get_data(
                        Utilities.StatType.playerWeekly, week, year)[
                        'players']
                    print week, len(results)
                    if results is None:
                        message = "Could not download teams."
                        Utilities.log(message, Utilities.populate_log)
                        return False

                    for value in results:
                        for stat, v in value['stats'].iteritems():
                            tup = (int(value['id']), float(stat),
                                   int(season_id), float(v))

                            if tup not in insert_tuples:
                                insert_tuples.append(tup)
                    season_id += 1

                except KeyError or TypeError, e:
                    Utilities.log_exception(e, Utilities.populate_log)
                    return False

            message = "Inserting values for year " + str(year) + " into the " \
                                                                 "database."

            print message
            Utilities.log(message, Utilities.populate_log)
            if not Utilities.populate_db(statement, Utilities.populate_log,
                                         insert_tuples):
                Utilities.log(
                    "Problem executing statement in the database. "
                    "Aborting.", Utilities.populate_log)

                return False
        return True

    def populate_teams(self):
        statement = "Insert IGNORE into Teams (teamID, name, teamNumber) " \
                    "values (%s, %s, %s);"

        try:
            results = self.provider.get_data(
                Utilities.StatType.teams)['NFLTeams']

            if results is None:
                message = "Could not download teams."
                Utilities.log(message, Utilities.populate_log)
                return False

            insert_tuples = []
            team_number = 1
            for value in results:
                if str(value['code']) == 'JAC':
                    value['code'] = 'JAX'

                insert_tuples.append((str(value['code']),
                                      str(value['fullName']), team_number))

                team_number += 1

            if not Utilities.populate_db(statement, Utilities.populate_log,
                                         insert_tuples):
                Utilities.log(
                    "Problem executing statement in the database. "
                    "Aborting.", Utilities.populate_log)

                return False

        except TypeError or KeyError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False
        return True

    @staticmethod
    def populate_seasons(start=2010, end=2016):
        season_id = Utilities.pull_from_db("select max(seasonId) from Season;",
                                           Utilities.populate_log)

        if season_id is None:
            season_id = 0
        else:
            try:
                season_id = season_id[0][0]
            except IndexError, e:
                Utilities.log_exception(e, Utilities.populate_log)
                return False

        statement = 'insert IGNORE into Season (SeasonId, week, seasonYear) ' \
                    'values ( %s, %s, %s)'

        insert_tuples = []
        for i in range(start, end):
            for j in range(1, 18):
                insert_tuples.append(((season_id + j), int(j), int(i)))
            season_id += 17

        if not Utilities.populate_db(statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log('Problem executing statement in the database. '
                          'Aborting.', Utilities.populate_log)

            return False
        return True

    def populate_weather(self):
        Utilities.log('Populating the weather and game conditions.',
                      Utilities.populate_log)

        # pull current weeks weather information
        weather_data = self.provider.get_data(Utilities.StatType.weather)

        # db info statements
        location_id_statement = 'select stadium, locationId, turf ' \
                                'from TeamLocations;'

        game_statement = 'select g.seasonId, g.homeTeam, g.awayTeam ' \
                         'from Games g, Season s where s.seasonId = ' \
                         'g.seasonId and s.week = %s and s.seasonYear = %s;'

        # db insert statement
        statement = 'REPLACE into GameConditions (gameId, locationId, ' \
                    'lowTemp, highTemp, isDome, forecast, windSpeed, turf)' \
                    'values (%s, %s, %s, %s, %s, %s, %s, %s);'

        # get location information
        results = Utilities.pull_from_db(location_id_statement,
                                         Utilities.populate_log)
        if not results:
            Utilities.log('Cannot pull stadium info from the database.',
                          Utilities.populate_log)
            return False

        stadiums = {}
        for tup in results:
            stadiums[tup[0]] = (int(tup[1]), tup[2])

        # get game information
        results = Utilities.pull_from_db(game_statement, Utilities.populate_log,
                                         (int(weather_data['Week']),
                                          Utilities.get_current_season()
                                          ))

        if not results:
            Utilities.log('Cannot pull game info from the database.',
                          Utilities.populate_log)
            return False

        games = {}
        for tup in results:
            games[(tup[1], tup[2])] = int(tup[0])

        # for each game, build tuple
        insert_tuples = []
        for key, value in weather_data['Games'].iteritems():
            if value['homeTeam'] == 'JAC':
                value['homeTeam'] = 'JAX'
            if value['awayTeam'] == 'JAC':
                value['awayTeam'] = 'JAX'

            # Hack until I can get the locationId from each game into a .csv
            # file from 2010 - 2015
            if value['stadium'] == 'LP Field':
                value['stadium'] = 'Nissan Stadium'
            new_tup = (games[(value['homeTeam'], value['awayTeam'])],
                       stadiums[value['stadium']][0], int(value['low'] or 0),
                       int(value['high'] or 0), int(value['isDome']),
                       str(value['forecast'] or 'NULL'),
                       int(value['windSpeed'] or 0),
                       stadiums[value['stadium']][1])

            insert_tuples.append(new_tup)

        # insert tuples into the database. Replace them if they already exist
        if not Utilities.populate_db(statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log('Problem executing statement in the database. '
                          'Aborting.', Utilities.populate_log)

            return False

        Utilities.log(
            'Finished populating the weather and game conditions.',
            Utilities.populate_log)
        return True

    @staticmethod
    def populate_locations():
        get_statement = "select teamId, name from Teams;"
        put_statement1 = "Insert ignore into TeamLocations (locationId, " \
                         "teamId, " \
                         "Stadium, turf) values (%s, %s, " \
                         "%s, %s);"

        put_statement2 = "Insert ignore into TurfTypes (turf) values (%s);"

        try:
            location_id = 1
            stadiums = [line.strip('\r\n').split(',') for line in open(
                Utilities.stadium_file)]

            teams_tuples = Utilities.pull_from_db(get_statement,
                                                  Utilities.populate_log
                                                  )
            teams_dict = {}
            for team in teams_tuples:
                teams_dict[team[1]] = team[0]

            insert_tuples1 = []
            insert_tuples2 = []
            for stadium in stadiums:
                tup = (location_id, teams_dict[stadium[2]], stadium[0],
                       stadium[1])
                insert_tuples1.append(tup)
                if (stadium[1],) not in insert_tuples2:
                    insert_tuples2.append((stadium[1],))

                location_id += 1

            if not Utilities.populate_db(put_statement1, Utilities.populate_log,
                                         insert_tuples1):
                Utilities.log("Couldn't insert stadiums into the database.",
                              Utilities.populate_log)
                return False

            if not Utilities.populate_db(put_statement2, Utilities.populate_log,
                                         insert_tuples2):
                Utilities.log("Couldn't insert turf into the database.",
                              Utilities.populate_log)
                return False
            return True

        except KeyError or TypeError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False


if __name__ == '__main__':
    populator = PopulateNFLDB()
    populator.populate_games_from_data()
