import datetime
import os.path

from src.wrapper_classes import DbMaintenance


# ----------------------- start default config and data paths ---------------- #
config_path = '../config_files/'

data_path = '../data'
schedule_data_path = os.path.join(data_path, 'schedules')
point_breakdown_path = os.path.join(data_path, 'point_breakdowns')
stadium_file = os.path.join(data_path, 'stadiums/stadiums.csv')
# ----------------------- end default config and data paths ------------------ #


# --------------------------- start logging utilities ------------------------ #
log_path = '../logs/'
db_log_file = os.path.join(log_path, 'dbMaintenanceLog.txt')
populate_log = os.path.join(log_path, 'populateDBLog.txt')
stat_provider_log = os.path.join(log_path, 'StatisticsProviderLog.txt')
extract_log = os.path.join(log_path, 'extractLog.txt')


def log(message, outfile='./log.txt'):
    with open(outfile, 'a') as f:
        f.write(str(datetime.datetime.now()) + ': ' + message.strip('\r\n') +
                '\n')


# A simple extension to uniformly log exceptions
def log_exception(e, log_file):
    template = "Exception: {0}. Arguments: {1!r}"
    message = template.format(type(e).__name__, e.args)
    log(message, log_file)
# -------------------------- end logging urilities --------------------------- #


# ------------------- start time conversion helper methods ------------------- #
def convert_to_24(time):
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
    global current_week
    current_week = new_week
    return current_week


def update_season(new_season):
    global current_season
    current_season = new_season
    return current_season


def get_current_season():
    global current_season
    return current_season
# -------------------- end season and week helper methods -------------------- #


# -------------------------- start Common db calls --------------------------- #
db_config = os.path.join(config_path, 'config.yml')
db = DbMaintenance.DbMaintenance()
db.import_db_config(db_config)


def import_db_config(config_file):
    return db.import_db_config(config_file)


def execute_procedure(procedure_name, args, log_file):
    log('Entering execute_procedure.', log_file)

    global db
    if db.execute_stored_procedure(procedure_name, args):
        data = db.get_results(stored=True)
    else:
        log('Could not execute the stored procedure.', log_file)
        data = []
    db.close_connection()
    log('Entering execute_procedure.', log_file)
    return data


def populate_db(statement, log_file, values):
    log('Entering populate_db.', log_file)

    global db
    if not db.prepare_statement(statement):
        log("Could not prepare statement.", log_file)
        return False

    if not db.execute_statement(values=values, commit=True):
        log("Could not execute statement.", log_file)
        return False

    db.close_connection()

    log('Exiting populate_db.', log_file)
    return True


def pull_from_db(statement, log_file, values_list=None):
    log('Entering pull_from_db.', log_file)

    global db
    results = None
    if values_list:
        db.prepare_statement(statement)
    if db .execute_statement(statement=statement, values=values_list):
        results = db.get_results()
    else:
        log("Could not execute statement.", log_file)

    db.close_connection()

    log('Exiting pull_from_db.', log_file)
    return results
# --------------------------- end Common db calls ---------------------------- #


# -------------------------- start statType enum class ----------------------- #
class StatType:
    playerInfo, statistics, playerWeekly, weather, injury, games, teams = \
        range(7)

    def __init__(self):
        pass
# ----------------------- end statType enum class ---------------------------- #


# ----------------------- start position enum class -------------------------- #
class Position:
    quarterback, running_back, kicker, defense, wide_receiver = range(5)
    tight_end = wide_receiver

    def __init__(self):
        pass
# ------------------------ end position enum class --------------------------- #
