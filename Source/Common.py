import datetime
import os.path

# DEFAULT LOG FILES
log_path = './'
config_path = './'
db_config = os.path.join(config_path, 'config.yml')
db_log_file = os.path.join(log_path, 'dbMaintenanceLog.txt')
populate_log = os.path.join(log_path, 'populateDBLog.txt')
stat_provider_log = os.path.join(log_path, 'StatisticsProviderLog.txt')


# A simple log function that just appends to a log file
def log(message, outfile='./log.txt'):
    with open(outfile, 'a') as f:
        f.write(str(datetime.datetime.now()) + ': ' + message.strip('\r\n') +
                '\n')


# A method to convert from valid 12 hour time to 24 hour time
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


class StatType:
    playerInfo, statistics, playerWeekly, weather, injury, games = range(6)

    def __init__(self):
        pass
