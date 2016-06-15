#!/usr/bin/python
import json
from Common import StatType
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
            for week in range(1, 18):
                # Get stats JSON file
                results = json.loads(self.provider.get_data(
                    StatType.playerInfo, week, season))['players']

                # build statement
                statement1 = "insert IGNORE into Players (playerId, " \
                             "firstName, lastName, position) values "
                insert_tuples1 = []
                statement2 = "insert IGNORE into PlayerTeam(playerId, " \
                             "teamId) values "
                insert_tuples2 = []
                for value in results:
                    tup = '(' + str(value['id']) + ',"' + \
                          str(value['firstName']) + '","' + \
                          str(value['lastName']) + '","' + \
                          str(value['position']) + '")'
                    insert_tuples1.append(tup)
                    if str(value['teamAbbr']) != '':
                        insert_tuples2.append('(' + str(value['id']) + ',"' +
                                              str(value['teamAbbr']) + '")')
                statement1 += ','.join(insert_tuples1)
                statement2 += ','.join(insert_tuples2)

                # Execute Statements
                self.populate_db(statement1)
                self.populate_db(statement2)

    def populate_stats(self):
        # Get stats JSON file
        result = json.loads(self.provider.get_data(
            StatType.statistics))['stats']

        # build statement
        statement = "insert IGNORE into Statistics (statID, name) values "
        insert_tuples = []
        for value in result:
            insert_tuples.append('(' + str(value['id']) + ",'" +
                                 str(value['name']) + "')")
        tuples_string = ','.join(insert_tuples)
        statement += tuples_string

        # Execute Statement
        self.populate_db(statement)

    def populate_games(self):
        this = self.junk
        this += this
        return

    def populate_injury_report(self):
        this = self.junk
        this += this
        return

    def populate_player_stats(self):
        #  Fill the players stats table for the last five season
        season_id = 1
        for year in range(2010, 2016):
            for week in range(1, 18):
                # Get stats JSON file
                results = json.loads(self.provider.get_data(
                    StatType.playerWeekly, week, year))['players']

                # Build statement
                statement = "insert IGNORE into PlayerStats (playerId, " \
                            "statId, Seasonid, statValue) values "
                insert_tuples = []
                for value in results:
                    for stat, v in value['stats'].iteritems():
                        tup = "(" + str(value['id']) + "," + str(stat) + \
                              "," + str(season_id) + "," + str(v) + ")"

                        insert_tuples.append(tup)
                statement += ','.join(insert_tuples)

                # Execute Statement
                self.populate_db(statement)
                season_id += 1
        return

    def populate_teams(self):
        # Get stats JSON file
        results = json.loads(self.provider.get_data(
            StatType.playerInfo))['players']
        # build statement
        statement = "insert IGNORE into Teams (teamID, name) values "
        insert_tuples = []
        for value in results:
            if str(value['teamAbbr']) != '':
                tup = "('" + str(value['teamAbbr']) + "','filler')"
                insert_tuples.append(tup)
        statement += ','.join(insert_tuples)

        # Execute Statement
        self.populate_db(statement)

    def populate_seasons(self):
        # Build Statement
        season_id = 0
        statement = "insert ignore into Season (SeasonId, week, year) values "
        insert_tuples = []
        # 2010-2015 Seasons
        for i in range(2010, 2016):
            # Weeks 1-17
            for j in range(1, 18):
                tup = '(' + str(season_id + j) + ',' + str(j) + ',' + \
                      str(i) + ')'
                insert_tuples.append(tup)
            season_id += 17
        statement += ','.join(insert_tuples)

        # Execute Statement
        self.populate_db(statement)

    def populate_weather(self):
        this = self.junk
        this += this
        return

    def populate_db(self, statement):
        # Add logic to verify input maybe?
        self.DB.execute_statement(statement)


if __name__ == '__main__':
    populator = PopulateNFLDB()
    populator.populate_players()
    populator.populate_player_stats()
