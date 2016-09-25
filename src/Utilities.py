import datetime
import os.path


# ----------------------- start default config and data paths ---------------- #
base_dir = '/home/derrick/Documents/customModules/nflStatsProj/'
config_path = os.path.join(base_dir, 'config_files/')

data_path = os.path.join(base_dir, 'data')
schedule_data_path = os.path.join(data_path, 'schedules')
point_breakdown_path = os.path.join(data_path, 'point_breakdowns')
stadium_file = os.path.join(data_path, 'stadiums/stadiums.csv')
# ----------------------- end default config and data paths ------------------ #

# ----------------------- Default db config file path ------------------------ #
db_config = os.path.join(config_path, 'config.yml')

# --------------------------- start logging utilities ------------------------ #
log_path = os.path.join(base_dir, 'logs/')
db_log_file = os.path.join(log_path, 'dbMaintenanceLog.txt')
populate_log = os.path.join(log_path, 'populateDBLog.txt')
stat_provider_log = os.path.join(log_path, 'StatisticsProviderLog.txt')
extract_log = os.path.join(log_path, 'extractLog.txt')
driver_log = os.path.join(log_path, 'driverLog.txt')
class_log = os.path.join(log_path, 'classifierLog.txt')


def log(message, outfile='./log.txt'):
    """
    A simple logging function that prepends a timestamp to ``message`` and \
    writes it to ``outfile``.

    :param message: a string containing the message to be printed to \
    ``outfile``.
    :param outfile: A string with the absolute path to a file to be written to.
    """

    with open(outfile, 'a') as f:
        f.write(str(datetime.datetime.now()) + ': ' + message.strip('\r\n') +
                '\n')


# A simple extension to uniformly log exceptions
def log_exception(e, log_file):
    """
    A simple logging function that prepends a timestamp to the provided \
    exception type and exception arguments writes it to ``outfile``.

    :param e: An exception object.
    :param log_file: A string with the absolute path to a file to be written to.
    """

    template = "Exception: {0}. Arguments: {1!r}"
    message = template.format(type(e).__name__, e.args)
    log(message, log_file)
    log(str(e), log_file)
# -------------------------- end logging utilities --------------------------- #


# ------------------- start time conversion helper methods ------------------- #
def convert_to_24(time):
    """
    A function to convert from meridiem time(AM/PM) to universal time (24 hour).

    :param time: A string representation of the time in 12 hour form. Ex. \
    '11:00 AM'

    :return: A string representation of the time in 24 hour format.
    """

    time, meridiem = time.split(' ')

    time_list = time.split(':')
    if len(time_list) == 2:
        hours, minutes = time_list
        seconds = '00'
    elif len(time_list) == 3:
        hours, minutes, seconds = time_list
    else:
        return None
    if meridiem == 'PM' and int(hours) != 12:
        hours = str(int(hours) + 12)
    elif meridiem == 'AM' and int(hours) == 12:
        hours = '00'
    time = ":".join([hours, minutes, seconds])

    return time
# ------------------- end time conversion helper methods --------------------- #


# ------------------- start season and week helper methods ------------------- #
current_season = 2016
current_week = 1
starting_year = 2010


def update_week(new_week):
    """
    An optional setter function for the current_week global variable. While \
    not required, the use of this function is preferred because it tests the \
    input for basic validity. Future refactoring with transform the underling \
    global variable into a class property.

    :return int: The new week if ``new_week`` is a valid update. I.E. \
    `new_week`` is an int an 1 <= `new_week`` <= 17
    :return int: -1 otherwise
    """
    global current_week
    current_week = new_week
    return current_week


def update_season(new_season):
    """
    An optional setter function for the current_season global variable. While \
    not required, the use of this function is preferred because it tests the \
    input for basic validity. Future refactoring with transform the underling \
    global variable into a class property.

    :return int: The new nfl season if ``new_season`` is a valid update
    :return int: -1 otherwise
    """

    global current_season
    if not isinstance(new_season, int):
        return -1
    current_season = new_season
    return current_season


def get_current_season():
    """
    An optional getter function. Currently this method is not very useful,
    because it just returns the value of a global variable, but future
    refactoring will encapsulate the current season attribute.

    :return int: The current nfl season. The default value is 2010.
    """

    global current_season
    return current_season


def get_current_week():
    """
    An optional getter function. Currently this method is not very useful,
    because it just returns the value of a global variable, but future
    refactoring will encapsulate the current week attribute.

    :return int: The current week in the nfl season. The default value is 1.
    """

    global current_week
    return current_week


# -------------------- end season and week helper methods -------------------- #

# -------------------------- start statType enum class ----------------------- #
class StatType:
    """
        StatType enum class with playerInfo, statistics, playerWeekly, weather,
        injury, games, teams, byes.
    """
    playerInfo, statistics, playerWeekly, weather, injury, games, teams, byes =\
        range(8)

    def __init__(self):
        pass
# ----------------------- end statType enum class ---------------------------- #


# ----------------------- start position enum class -------------------------- #
class Positions:
    """
       Positions enum class with quarterback, running_back, kicker, defense
       wide_receiver, and tight_end
    """
    quarterback, running_back, kicker, defense, wide_receiver = range(5)
    tight_end = wide_receiver

    positions_dict = {quarterback: 'QB',
                      running_back: 'RB',
                      kicker: 'K',
                      defense: 'DEF',
                      wide_receiver: 'WR'}

    def __init__(self):
        pass

    @staticmethod
    def get_positions():
        """

        :return: a dictionary containing the enum and the string \
        representation of each position.
        """
        return Positions.positions_dict

# ------------------------ end position enum class --------------------------- #
