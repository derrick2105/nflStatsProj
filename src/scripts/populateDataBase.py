#!/usr/bin/python
from os import listdir, path

import Utilities
from wrapper_classes.DbMaintenance import DbMaintenance
from wrapper_classes.StatisticsProvider import NFLStatsProvider as Provider


####
#   Current issues
#   Issue where LP Field is used instead of Nissan Stadium
#   Current implementation will improperly assign locationId for
#   international games
####

class PopulateNFLDB:
    """
    This is a collection of the methods needed to populate all of the tables in
    the database. If you run this script as a python script, it will call the
    populate_all method and return after completion.

    Example Usage:

    .. testcode::

        from scripts import PopulateNFLDB
        populator = PopulateNFLDB()
        populator.populate_all()

    """
    def __init__(self):
        self.DB = DbMaintenance()
        self.provider = Provider()
        self.DB.import_db_config(Utilities.db_config)

    def __del__(self):
        del self.DB
        del self.provider

    def populate_all(self):
        """
        This is a method that runs all of the below methods with their default
        parameters. Use this method to populate an empty database will all of
        data from season i s.t. i in [2010, 2016).

        """
        # Add all of the non player specific information.
        self.populate_seasons()
        self.populate_new_season(Utilities.current_season)
        self.populate_teams()
        self.populate_games_from_data(Utilities.schedule_data_path)
        self.populate_new_season_games()
        self.populate_stats()

        self.populate_locations()
        self.populate_weather()

        # Add each player, their statistics, and their injury report.
        # Currently only adds the latest injury report.
        self.populate_players()
        self.populate_player_stats()
        self.populate_injury_report()

    def populate_players(self):
        """
        This is a method to populate the Players table in the database. It
        uses a statisticsProvider object to download player information from
        the NFL.com API

        :return True: If the player table is successfully populated.
        :return False: Otherwise.

        """
        statement1 = "Insert Ignore into Players (playerId, firstName, " \
                     "lastName, position) values (%s, %s, %s, %s);"

        statement2 = "Replace into PlayerTeam(playerId, teamId)" \
                     " values (%s, %s);"

        insert_tuples1 = []
        insert_tuples2 = []

        Utilities.log("Downloading players.", Utilities.populate_log)

        try:
            results = self.provider.get_data(Utilities.StatType.playerInfo,
                                             season=Utilities.current_season)[
                                             'players']

            for value in results:
                tup = (int(value['id']), str(value['firstName']),
                       str(value['lastName']), str(value['position']))

                if tup not in insert_tuples1:
                    insert_tuples1.append(tup)
                if str(value['teamAbbr']) == '':
                    value['teamAbbr'] = None
                tup2 = (int(value['id']), str(value['teamAbbr'] or None))
                if tup2 not in insert_tuples2:
                    insert_tuples2.append(tup2)

        except TypeError or KeyError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False

        message = "Inserting values into the database."

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
        """
        his is a method to populate the PlayStatistics table in the
        database. It uses a statisticsProvider object to download list of
        Statistical information from the NFL.com API

        :return True: if the statistics table is successfully populated.
        :return False: otherwise

        """
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
        """
        This is a method to populate the Games table in the
        database with a new season of games. It uses a statisticsProvider
        object to download list of Games from the NFL.com API

        :return True: if the Games table is successfully populated.
        :return False: Otherwise.

        """

        get_statement1 = "Select MAX(seasonId) from Season;"
        get_statement2 = "Select MAX(seasonId) from Games;"
        put_statement1 = "Insert Ignore into Games (seasonID, homeTeam, " \
                         "awayTeam, gameTime) values (%s, %s, %s, %s);"

        put_statement2 = "Insert Ignore into ByeWeeks (seasonId, teamId) " \
                         "values (%s, %s);"

        max_season_id = Utilities.pull_from_db(get_statement1,
                                               Utilities.populate_log)

        if max_season_id:
            max_season_id = max_season_id[0][0]
        else:
            max_season_id = 0

        games_max_id = Utilities.pull_from_db(get_statement2,
                                              Utilities.populate_log)

        if games_max_id:
            games_max_id = games_max_id[0][0]
        else:
            games_max_id = 0

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

                        insert_tuples2.append(tup)

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
    def populate_games_from_data(data_path=None):
        """
        This is a method to populate the Games table in the database with
        old games. It reads in the .csv files located at data_path and
        inserts each game into the database.

        :param data_path: A string that denotes the path to a directory \
        containing game information from 2010 - 2016. Default value of \
        'nflStatsProj/data/schedules/'

        :return True: If the Games table is successfully populated.
        :return False: Otherwise.

        """

        if not data_path:
            data_path = Utilities.schedule_data_path
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
        """
        This is a method to populate the Season table in the database with
        a new season.

        :param year: an int that represents a season year to insert into the \
        database. Defaults to 2016.

        :return True: If  year == current_season + 1 and the new season is \
        successfully inserted into the database.
        :return False: Otherwise.

        """

        if not year:
            year = Utilities.get_current_season() + 1

        if year - Utilities.get_current_season() == 1:
            Utilities.update_season(year)
        else:
            Utilities.log('New season year is too far in the future.',
                          Utilities.populate_log)
            return False

        Utilities.update_week(1)
        return self.populate_seasons(year, year + 1)

    def populate_injury_report(self):
        """
        This is a method to populate the InjuryReport table in the database.

        :return True: if the InjuryReport table is successfully populated.
        :return False: Otherwise.

        """

        get_statement = 'select playerId from Players;'
        insert_statement = 'REPLACE into InjuryReport (playerId, ' \
                           'injurySeverity) values (%s, %s);'

        insert_tuples = []
        id_tuples = Utilities.pull_from_db(get_statement,
                                           Utilities.populate_log)

        for id_tup in id_tuples:

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

        Utilities.log(message, Utilities.populate_log)
        if not Utilities.populate_db(insert_statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log("Problem executing statement in the database. "
                          "Aborting.", Utilities.populate_log)

            return False
        return True

    def populate_player_stats(self, week=None, year=None):
        """
        This is a method to populate the player_stats table in the database
        with the stats from week, year or all weeks from years 2010 - 2015. It
        uses a StatsProvider object to download the player_stats information
        from the NFL.com API.

        :param week: an int that represents the week in which you want to \
        download. 1 <= week <= 17. If week is None, insert all the stats \
        from 1 week to week 17.

        :param year: an int that represents the year in which you want to \
        download the stats. 2010 <= year <= Utilities.current_season. \
        If year is None, then insert all stats from 2010 - 2015.

        :return True: If  the player_stats table is successfully populated.
        :return False: Otherwise

        """

        start_week, end_week, start_year, end_year = \
            self._validate_week_and_year(week, year)

        if start_week == 0:
            return False

        if start_year == 2010 and start_week == 1:
            season_id = 1
        else:
            season_id = self._get_season_id(week, year)

        statement = "Insert IGNORE into PlayerStats (playerId, statId, " \
                    "Seasonid, statValue) values (%s, %s, %s, %s);"

        insert_tuples = []
        for year in xrange(start_year, end_year):
            message = "Downloading player stats from " + str(year)
            Utilities.log(message, Utilities.populate_log)
            for week in xrange(start_week, end_week):
                new_tuples = self._pull_player_stats_weekly(year, week,
                                                            season_id)

                if not new_tuples:
                    message = "Couldn't download players for week: " + str(week)
                    message += " year: " + str(year)

                    Utilities.log(message, Utilities.populate_log)
                    return False

                else:
                    insert_tuples.extend(new_tuples)

                season_id += 1

        message = 'Inserting player stats into db.'
        Utilities.log(message, Utilities.populate_log)
        if not Utilities.populate_db(statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log("Problem executing statement in the database. "
                          "Aborting.", Utilities.populate_log)

            return False
        return True

    def populate_teams(self):
        """
        This is a method to populate the Teams table in the database with a
        range of seasons. It uses a StatsProvider object to download the
        playerTeams information from the NFL.com API.

        :return True: If  the Teams table is successfully populated.
        :return False: Otherwise.

        """

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

            # Needed for international games
            insert_tuples.append(('NFL', 'NFL international', '33'))
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
        """
        This is a method to populate the Season table in the database with a
        range of seasons.

        :param start: an int that represents a start year to insert into the \
        database.

        :param end: an int that represents an end year to insert into the \
        database.

        :return True: If  start == current_season + 1 and start <= end and \
        the new seasons are successfully inserted into the database
        :return False: Otherwise

        """

        Utilities.log('Entering populate_seasons', Utilities.populate_log)
        season_id = Utilities.pull_from_db("select max(seasonId) from Season;",
                                           Utilities.populate_log)

        if start > end or start > Utilities.get_current_season() + 1:
            Utilities.log('Starting and end index is out of range.',
                          Utilities.populate_log)
            return False
        if season_id is None or season_id[0][0] is None:
            season_id = 0
        else:
            try:
                season_id = season_id[0][0]
            except IndexError, e:
                Utilities.log_exception(e, Utilities.populate_log)
                return False

        statement = 'insert IGNORE into Season (SeasonId, week, seasonYear) ' \
                    'values ( %s, %s, %s);'

        insert_tuples = []
        for i in range(start, end):
            for j in range(1, 18):
                insert_tuples.append(((season_id + j), int(j), int(i)))
            season_id += 17

        if not Utilities.populate_db(statement, Utilities.populate_log,
                                     insert_tuples):
            Utilities.log('Problem executing statement in the database. '
                          'Aborting.', Utilities.populate_log)

            Utilities.log('Exiting populate_seasons', Utilities.populate_log)
            return False
        Utilities.log('Exiting populate_seasons', Utilities.populate_log)
        return True

    def populate_weather(self):
        """
        This is a method to populate the game_conditions table in the
        database. It uses a statisticsProvider object to download the
        current week of weather predictions and game conditions (like
        whether or not a game is being played in a dome.

        :return True: If the game_conditions are successfully inserted \
        into the database.
        :return False: Otherwise

        """
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
        """
        This is a method to populate the TeamLocations and TurfType tabled
        in the database. It uses the default stadium data directory (
        'nflStatsProj/data/stadiums') to populate the teams stadium, and the
        turfTypes table with the different types of turf that players will
        play on.

        :return True: If the TeamLocations and TurfTypes tables are \
        successfully updated.
        :return False: Otherwise.

        """

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

            if not Utilities.populate_db(put_statement2,
                                         Utilities.populate_log,
                                         insert_tuples2):
                Utilities.log("Couldn't insert turf into the database.",
                              Utilities.populate_log)
                return False
            return True

        except KeyError or TypeError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return False

    def _pull_player_stats_weekly(self, year, week, season_id):
        insert_tuples = []
        try:
            results = self.provider.get_data(
                Utilities.StatType.playerWeekly, week, year)[
                'players']
            if results is None:
                error_message = "Could not download players."
                Utilities.log(error_message, Utilities.populate_log)
                return []

            for value in results:
                for stat, v in value['stats'].iteritems():
                    tup = (int(value['id']), float(stat),
                           int(season_id), float(v))

                    if tup not in insert_tuples:
                        insert_tuples.append(tup)

        except KeyError or TypeError, e:
            Utilities.log_exception(e, Utilities.populate_log)
            return []

        return insert_tuples

    @staticmethod
    def _get_season_id(week, year):
        statement = "select seasonId from Season where week = %s and " \
                    "seasonYear = %s;"
        res = Utilities.pull_from_db(statement, Utilities.populate_log,
                                     (week, year))
        if not res:
            Utilities.log("Couldn't set the correct seasonId",
                          Utilities.populate_log)
            return None
        else:
            return res[0][0]

    @staticmethod
    def _validate_week_and_year(week, year):
        if not week:
            start_week, end_week = 1, 18
        else:
            if type(week) is not int or week < 1 or week >= 18:
                Utilities.log("Week must be an integer such that 1 <= week <= "
                              "17", Utilities.populate_log)
                return 0, 0, 0, 0
            start_week, end_week = week, week + 1

        if not year:
            start_year, end_year = Utilities.starting_year, Utilities. \
                current_season
        else:
            if type(year) is not int or year < Utilities.starting_year or \
                            year > Utilities.current_season:
                error_message = "Year must be an integer such that " + \
                                Utilities.starting_year + " <= year <= " + \
                                str(Utilities.current_season)

                Utilities.log(error_message, Utilities.populate_log)
                return 0, 0, 0, 0

            start_year, end_year = year, year + 1
        return start_week, end_week, start_year, end_year

if __name__ == '__main__':
    populator = PopulateNFLDB()
    populator.populate_player_stats(1, 2016)
