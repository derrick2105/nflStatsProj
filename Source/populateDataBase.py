#!/usr/bin/python
import Common
from StatisticsProvider import NFLStatsProvider as Provider
from DbMaintenance import DbMaintenance
from os import listdir, path


####
# TODO:
#   1. Write the Weather method
#   2. Refactor the db schema to add turf info to the teamLocation table
#   3. update populate_teams to reflect changes to the db
#   4. update the gameCondition schema and weather method to include a gameId
####

class PopulateNFLDB:
    def __init__(self):
        self.DB = DbMaintenance()
        self.provider = Provider()
        self.DB.import_db_config(Common.db_config)

    def __del__(self):
        del self.DB
        del self.provider

    def populate_all(self):
        # Add all of the non player specific information.
        self.populate_seasons()
        self.populate_teams()
        self.populate_games_from_data(Common.schedule_data_path)
        self.populate_new_season_games()
        self.populate_stats()
        self.populate_weather()

        # Add each player, their statistics, and their injury report.
        # Currently only adds the latest injury report.
        self.populate_players()
        self.populate_player_stats()
        self.populate_injury_report()

    def populate_players(self):
        # Test this before sending it to Zach.
        statement1 = "insert IGNORE into Players (playerId, firstName, " \
                     "lastName, position) values (%s, %s, %s, %s);"

        statement2 = "insert replace into PlayerTeam(playerId, teamId)" \
                     " values (%s, %s);"

        for season in range(2010, 2016):
            message = "Downloading players from " + str(season)
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
                    Common.log_exception(e, Common.populate_log)
                    return False

            message = "Inserting values for season: " + str(season) +\
                      " into the database."

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

        statement = "INSERT IGNORE into Statistics (statID, stat_name) values" \
                    " (%s, %s);"

        insert_tuples = []
        try:
            for value in result:
                insert_tuples.append((int(value['id']), str(value['name'])))

            if not self.populate_db(statement, insert_tuples):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False

        except TypeError or KeyError, e:
            Common.log_exception(e, Common.populate_log)
            return False

        return True

    def populate_new_season_games(self):
        get_statement1 = "Select MAX(seasonId) from Season;"
        get_statement2 = "Select MAX(seasonId) from Games;"
        put_statement = "Insert into Games (seasonID, homeTeam, awayTeam, " \
                        "gameTime) values " \
                        "(%s, %s, %s, %s);"

        max_season_id = self.pull_from_db(get_statement1)[0][0]
        games_max_id = self.pull_from_db(get_statement2)[0][0]

        if max_season_id != games_max_id:
            # Possibly refactor this line. It can cause the db to become
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
                Common.log_exception(e, Common.populate_log)
                return False

        return True

    def populate_games_from_data(self, data_path=Common.schedule_data_path):
        start_year = 2010
        put_statement = "Insert ignore into Games (seasonId, homeTeam, " \
                        "awayTeam) values (%s, %s, %s);"

        try:
            # Assuming data_files have the naming convention <year>_sched.csv
            data_files = [file_name for file_name in sorted(listdir(
                          data_path)) if path.isfile(path.join(data_path,
                                                               file_name))]

        except OSError, e:
            Common.log_exception(e, Common.populate_log)
            return False

        insert_tuples = []
        for file_name in data_files:
            try:
                offset = int(file_name[0:4]) - start_year
            except ValueError, e:
                Common.log_exception(e, Common.populate_log)
                return False

            file_name = path.join(data_path, file_name)
            with open(file_name) as f:
                for line in f:
                    team_schedule = line.strip('\r\n').split(',')
                    try:
                        if team_schedule[0] == "WSH":
                            team_schedule[0] = "WAS"
                        for index in xrange(1, len(team_schedule)):
                            if team_schedule[index].upper() == "BYE":
                                continue
                            season_id = offset*17 + index
                            if team_schedule[index][0] == '@':
                                if team_schedule[index] == "@WSH":
                                    team_schedule[index] = "@WAS"
                                tup = (season_id, team_schedule[index][1:],
                                       team_schedule[0])
                            else:
                                if team_schedule[index] == "WSH":
                                    team_schedule[index] = "WAS"
                                tup = (season_id, team_schedule[0],
                                       team_schedule[index])

                            if tup not in insert_tuples:
                                insert_tuples.append(tup)

                    except IndexError, e:
                        Common.log_exception(e, Common.populate_log)
                        return False

        print "inserting games into the Database."
        if not self.populate_db(put_statement, insert_tuples):
            Common.log("Couldn't insert games int the database.",
                       Common.populate_log)

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
                Common.log_exception(e, Common.populate_log)
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
        statement = "Insert IGNORE into PlayerStats (playerId, statId, " \
                    "Seasonid, statValue) values (%s, %s, %s, %s);"

        for year in range(2010, 2016):
            message = "Downloading player stats from " + str(year)
            print message
            Common.log(message, Common.populate_log)
            insert_tuples = []
            for week in range(1, 18):
                try:
                    results = self.provider.get_data(
                        Common.StatType.playerWeekly, week, year)['players']
                    print week, len(results)
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
                    Common.log_exception(e, Common.populate_log)
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
            results = self.provider.get_data(Common.StatType.teams)['NFLTeams']
            if results is None:
                message = "Could not download teams."
                Common.log(message, Common.populate_log)
                return False

            insert_tuples = []
            for value in results:
                if str(value['code']) == 'JAC':
                    value['code'] = 'JAX'

                insert_tuples.append((str(value['code']),
                                      str(value['fullName'])))

            if not self.populate_db(statement, insert_tuples):
                Common.log("Problem executing statement in the database. "
                           "Aborting.", Common.populate_log)

                return False

        except TypeError or KeyError, e:
            Common.log_exception(e, Common.populate_log)
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
                Common.log_exception(e, Common.populate_log)
                return False

        statement = "insert IGNORE into Season (SeasonId, week, seasonYear) " \
                    "values ( %s, %s, %s)"

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
        # gameCondition table
        # locationId, lowTemp, highTemp, isDome, forecast, windSpeed, turf
        # json result per game
        # gameWeek, gameId, geoLat, windChill, domeImg, homeTeam, winner,
        # gameTime, largeImg, geoLong, tvStation, high, awayTeam, windSpeed,
        # mediumImg, low, stadium, isDome, forecast, gameDate, smallImg

        # pull current week information
        data = self.provider.get_data(Common.StatType.weather)

        # db info statements
        location_id_statement = 'select stadium, locationId from TeamLocations;'

        # Probable refactor to add turf info to the stadium table in the db
        # This is dumb, but I don't want to fuck with the Db schema right now.
        # get list of stadium info for turf portion
        results = self.pull_from_db(location_id_statement)
        if not results:
            message = 'Cannot pull stadium info from the database.'
            Common.log(message, Common.populate_log)
            return False

        stadiums = {}
        for tup in results:
            stadiums[tup[0]] = int(tup[1])

        for row in open(Common.stadium_file):
            line = row.strip('\r\n').split(',')
            stadiums[line[0]] = (stadiums[line[0]], line[1], line[2])

        # for each game, build tuple
        insert_tuples = []
        for key, value in data['Games'].iteritems():
            new_tup = (stadiums[value['stadium']][0], int(value['low'] or 0),
                       int(value['high'] or 0), int(value['isDome']),
                       value['forecast'], value['windSpeed'],
                       stadiums[value['stadium']][1])

            insert_tuples.append(new_tup)

        # insert tuples into the database. Replace them if they already exist

        return True

    def populate_locations(self):
        get_statement1 = "Select * from TeamLocations;"
        get_statement2 = "select teamId, name from Teams;"
        put_statement = "Insert into TeamLocations (locationId, teamId, " \
                        "Stadium) values (%s, %s, %s);"

        try:
            location_arr = self.pull_from_db(get_statement1)
            if location_arr:
                Common.log("The locations are already populated. Purge "
                           "locations and try again.", Common.populate_log)

                return False

            location_id = 1
            stadiums = [line.strip('\r\n').split(',') for line in open(
                Common.stadium_file)]

            teams_tuples = self.pull_from_db(get_statement2)
            teams_dict = {}
            for team in teams_tuples:
                teams_dict[team[1]] = team[0]

            insert_tuples = []
            for stadium in stadiums:
                tup = (location_id, teams_dict[stadium[2]], stadium[0])
                insert_tuples.append(tup)
                location_id += 1

            if not self.populate_db(put_statement, insert_tuples):
                Common.log("Couldn't insert stadiums into the database.",
                           Common.populate_log)
                return False
            return True

        except KeyError or TypeError, e:
            Common.log_exception(e, Common.populate_log)
            return False

    def populate_db(self, statement, values):
        if not self.DB.prepare_statement(statement):
            Common.log("Could not prepare statement.", Common.populate_log)
            return False

        if not self.DB.execute_statement(values=values, commit=True):
            Common.log("Could not execute statement.", Common.populate_log)
            return False

        self.DB.close_connection()
        return True

    def pull_from_db(self, statement, vals=None):
        results = None
        if vals:
            self.DB.prepare_statement(statement)
        if self.DB.execute_statement(statement=statement, values=vals):
            results = self.DB.get_results()
        else:
            Common.log("Could not execute statement.", Common.populate_log)

        self.DB.close_connection()
        return results

if __name__ == '__main__':
    populator = PopulateNFLDB()
    populator.populate_all()
