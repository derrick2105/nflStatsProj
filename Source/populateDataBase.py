#!/usr/bin/python
import Common
from StatisticsProvider import NFLStatsProvider as Provider
from DbMaintenance import DbMaintenance


####
# TODO:
# 1. write the locations method
# 2. Write the Weather method
###

class PopulateNFLDB:
    def __init__(self):
        self.DB = DbMaintenance()
        self.provider = Provider()
        self.junk = 1
        self.DB.import_db_config(Common.db_config)

    def __del__(self):
        del self.DB
        del self.provider

    def populate_all(self):
        # Add all of the non player specific information.
        self.populate_seasons()
        self.populate_teams()
        self.populate_games()
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

        statement2 = "insert IGNORE into PlayerTeam(playerId, teamId)" \
                     " values (%s, %s);"

        for season in range(2010, 2016):
            message = "Downloading players from " + str(season)
            print message
            Common.log(message, Common.populate_log)

            insert_tuples1 = []
            insert_tuples2 = []

            for week in range(1, 18):
                try:
                    results = self.provider.get_data(
                        Common.StatType.playerInfo, week, season)['players']

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
                    Common.log(str(e), Common.populate_log)
                    return False

            message = "Inserting values for season: " + str(season) +\
                      " into the database."

            print message
            Common.log(message, Common.populate_log)
            if not self.populate_db(statement1, insert_tuples1) or not \
                    self.populate_db(statement2, insert_tuples2):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False
        return True

    def populate_stats(self):
        result = self.provider.get_data(
            Common.StatType.statistics)['stats']

        statement = "INSERT IGNORE into Statistics (statID, name) values " \
                    "(%s, %s);"

        insert_tuples = []
        try:
            for value in result:
                insert_tuples.append((int(value['id']), str(value['name'])))

            if not self.populate_db(statement, insert_tuples):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False

        except TypeError or KeyError, e:
            Common.log(str(e), Common.populate_log)
            return False

        return True

    def populate_games(self):
        get_statement1 = "Select MAX(seasonId) from Season;"
        get_statement2 = "Select MAX(seasonId) from Games;"
        put_statement = "Insert into Games (seasonID, homeTeam, awayTeam, " \
                        "gameTime) values " \
                        "(%s, %s, %s, %s);"

        max_season_id = self.pull_from_db(get_statement1)[0][0]
        games_max_id = self.pull_from_db(get_statement2)[0][0]

        if max_season_id != games_max_id:
            # Possible refactor this line. It can cause the db to become
            # inconsistent
            games_max_id = max_season_id - 17
            try:
                results = self.provider.get_data(data_type=Common.StatType.games
                                                 )['Schedule']

                insert_tuples = []
                for result in results:
                    if result['homeTeam'] == 'JAC':
                        result['homeTeam'] = 'JAX'
                    if result['awayTeam'] == 'JAC':
                        result['awayTeam'] = 'JAX'
                    tup = (games_max_id + int(result['gameWeek']),
                           str(result['homeTeam']), str(result['awayTeam']),
                           str(Common.convert_to_24(result['gameTimeET'])))
                    insert_tuples.append(tup)

                print "Inserting into the Database"
                if not self.populate_db(put_statement, insert_tuples):
                    Common.log("Problem executing statement in the database..."
                               "Aborting.", Common.populate_log)

                    return False

            except TypeError or KeyError, e:
                Common.log(str(e), Common.populate_log)
                return False

        return True

    def populate_new_season(self, year):
        return self.populate_seasons(year, year+1)

    def populate_injury_report(self):

        get_statement = 'select playerId from Players;'
        insert_statement = 'REPLACE into InjuryReport (playerId, ' \
                           'injurySeverity) values (%s, %s);'
        insert_tuples = []
        print "Retrieving injury reports."
        count = 0
        id_tuples = self.pull_from_db(get_statement)
        tuple_count = float(len(id_tuples))
        for id_tup in id_tuples:
            count += 1
            if count % 100 == 0:
                print "Percentage of reports gathered so far: ", \
                       round(count * 100 / tuple_count, 2)

            try:
                stats = self.provider.get_data(
                    data_type=Common.StatType.injury, player_id=id_tup[0])

                insert_tuples.append((id_tup[0], str(stats['players'][0]
                                                     ['injuryGameStatus'])))
            except TypeError or KeyError, e:
                Common.log(str(e), Common.populate_log)
                return False

        message = "Inserting player Injury Statuses into the database."

        print message
        Common.log(message, Common.populate_log)
        if not self.populate_db(insert_statement, insert_tuples):
            Common.log("Problem executing statement in the database. "
                       "Aborting.", Common.populate_log)

            return False

        return True

    def populate_player_stats(self):
        season_id = 1
        insert_tuples = []
        statement = "Insert IGNORE into PlayerStats (playerId, statId, " \
                    "Seasonid, statValue) values (%s, %s, %s, %s);"

        for year in range(2014, 2016):
            message = "Downloading player stats from " + str(year)
            print message
            Common.log(message, Common.populate_log)
            for week in range(1, 18):
                try:
                    results = self.provider.get_data(
                        Common.StatType.playerWeekly, week, year)

                    if results is None:
                        message = "Could not download teams."
                        Common.log(message, Common.populate_log)
                        return False

                    for value in results:
                        for stat, v in value['stats'].iteritems():
                            tup = (int(value['id']), float(stat),
                                   int(season_id), float(v))

                            if tup not in insert_tuples:
                                insert_tuples.append(tup)
                    season_id += 1

                except KeyError or TypeError, e:
                    Common.log(str(e), Common.populate_log)
                    return False

            message = "Inserting values for year " + str(year) + " into the " \
                      "database."

            print message
            Common.log(message, Common.populate_log)
            if not self.populate_db(statement, insert_tuples):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False
        return True

    def populate_teams(self):
        statement = "insert IGNORE into Teams (teamID, name) values (%s, %s)"

        try:
            results = self.provider.get_data(Common.StatType.playerInfo)
            if results is None:
                message = "Could not download teams."
                Common.log(message, Common.populate_log)
                return False

            insert_tuples = []
            for value in results:
                if str(value['teamAbbr']) != '':
                    insert_tuples.append((str(value['teamAbbr']), 'filler'))

            if not self.populate_db(statement, insert_tuples):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False
        except TypeError or KeyError, e:
            Common.log(str(e), Common.populate_log)
            return False
        return True

    def populate_seasons(self, start=2010, end=2016):
        season_id = self.pull_from_db("select max(seasonId) from Season;")

        if season_id is None:
                season_id = 0
        else:
            try:
                season_id = season_id[0][0]
            except IndexError, e:
                Common.log(str(e), Common.populate_log)
                return False

        statement = "insert IGNORE into Season (SeasonId, week, year) values " \
                    "(%s, %s, %s)"

        insert_tuples = []
        for i in range(start, end):
            for j in range(1, 18):
                insert_tuples.append(((season_id + j), int(j), int(i)))
            season_id += 17

        if not self.populate_db(statement, insert_tuples):
            Common.log("Problem executing statement in the database. "
                       "Aborting.", Common.populate_log)

            return False
        return True

    # TODO
    def populate_weather(self):
        pass

    # TODO
    def populate_locations(self):
        pass

    def populate_db(self, statement, values):
        if not self.DB.prepare_statement(statement):
            Common.log("Could not prepare statement.", Common.populate_log)
            return False

        if not self.DB.execute_statement(values=values, commit=True):
            Common.log("Could not execute statement.", Common.populate_log)
            return False

        self.DB.close_connection()
        return True

    def pull_from_db(self, statement):
        results = None
        if self.DB.execute_statement(statement=statement):
            results = self.DB.get_results()
        else:
            Common.log("Could not execute statement.", Common.populate_log)

        self.DB.close_connection()
        return results

if __name__ == '__main__':
    populator = PopulateNFLDB()
    if not populator.populate_games():
        print "Aborting."
