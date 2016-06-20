#!/usr/bin/python
import json
import Common
from StatisticsProvider import NFLStatsProvider as Provider
from DbMaintenance import DbMaintenance


####
# TODO:
# 1. Add error catching to each call.
# 2. write the games, injury, and Weather methods
# 3. remove self.junk
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
        for season in range(2010, 2016):
            print "Inserting players from", season
            for week in range(1, 18):
                print "Week:", week
                results = json.loads(self.provider.get_data(
                    Common.StatType.playerInfo, week, season))['players']

                statement1 = "insert IGNORE into Players (playerId, " \
                             "firstName, lastName, position) values (%s, %s," \
                             " %s, %s);"

                insert_tuples1 = []
                statement2 = "insert IGNORE into PlayerTeam(playerId, teamId)" \
                             " values (%s, %s);"

                insert_tuples2 = []
                for value in results:
                    tup = (int(value['id']), str(value['firstName']),
                           str(value['lastName']), str(value['position']))

                    insert_tuples1.append(tup)
                    if str(value['teamAbbr']) != '':
                        insert_tuples2.append((int(value['id']),
                                               str(value['teamAbbr'])))

                if not self.populate_db(statement1, insert_tuples1) or not\
                        self.populate_db(statement2, insert_tuples2):

                    Common.log("Problem executing statement in the database. "
                               "Aborting.", Common.populate_log)

                    return False
        return True

    def populate_stats(self):
        result = json.loads(self.provider.get_data(
            Common.StatType.statistics))['stats']

        statement = "insert IGNORE into Statistics (statID, name) values " \
                    "(%s, %s);"

        insert_tuples = []
        for value in result:
            insert_tuples.append((int(value['id']), str(value['name'])))

        if not self.populate_db(statement, insert_tuples):
            Common.log("Problem executing statement in the database. "
                       "Aborting.", Common.populate_log)

            return False
        return True

    def populate_games(self):
        this = self.junk
        this += this

    def populate_injury_report(self):
        this = self.junk
        this += this

    def populate_player_stats(self):
        season_id = 1
        for year in range(2010, 2016):
            print "Inserting player stats from", year
            for week in range(1, 18):
                print "Week:", week
                results = json.loads(self.provider.get_data(
                    Common.StatType.playerWeekly, week, year))['players']

                statement = "insert IGNORE into PlayerStats (playerId, " \
                            "statId, Seasonid, statValue) values " \
                            "(%s, %s, %s, %)"

                insert_tuples = []
                for value in results:
                    for stat, v in value['stats'].iteritems():
                        tup = (int(value['id']), int(stat), int(season_id),
                               int(v))

                        insert_tuples.append(tup)

                if not self.populate_db(statement, insert_tuples):
                    Common.log("Problem executing statement in the database. "
                               "Aborting.", Common.populate_log)

                    return False
                season_id += 1
        return True

    def populate_teams(self):
        results = json.loads(self.provider.get_data(
            Common.StatType.playerInfo))['players']

        statement = "insert IGNORE into Teams (teamID, name) values (%s, %s)"

        insert_tuples = []
        for value in results:
            if str(value['teamAbbr']) != '':
                insert_tuples.append((str(value['teamAbbr']), 'filler'))

        if not self.populate_db(statement, insert_tuples):
            Common.log("Problem executing statement in the database. "
                       "Aborting.", Common.populate_log)

            return False
        return True

    def populate_seasons(self):
        season_id = 0
        statement = "insert IGNORE into Season (SeasonId, week, year) values " \
                    "(%s, %s, %s)"

        insert_tuples = []
        for i in range(2010, 2016):
            for j in range(1, 18):
                insert_tuples.append(((season_id + j), int(j), int(i)))
            season_id += 17

        if not self.populate_db(statement, insert_tuples):
            Common.log("Problem executing statement in the database. "
                       "Aborting.", Common.populate_log)

            return False
        return True

    def populate_weather(self):
        this = self.junk
        this += this
        return

    def populate_db(self, statement, values):
        if not self.DB.prepare_statement(statement):
            Common.log("Could not prepare statement.", Common.populate_log)
            return False

        if not self.DB.execute_statement(values, commit=True):
            Common.log("Could not execute statement.", Common.populate_log)
            return False
        return True

if __name__ == '__main__':
    populator = PopulateNFLDB()
    if not populator.populate_players():
        print "Aborting."
    else:
        if not populator.populate_player_stats():
            print "Aborting."
