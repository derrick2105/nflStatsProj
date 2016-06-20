import datetime
import os.path

# DEFAULT LOG FILES
log_path = './'
config_path = "./"
db_config = os.path.join(config_path, "config.yml")
db_log_file = os.path.join(log_path, 'dbMaintenanceLog.txt')
populate_log = os.path.join(log_path, 'populateDBLog.txt')
stat_provider_log = os.path.join(log_path, 'StatisticsProviderLog.txt')


# A simple log function that just appends to a log file
def log(message, outfile='./log.txt'):
    with open(outfile, 'a') as f:
        f.write(str(datetime.datetime.now()) + ': ' + message.strip('\r\n') +
                '\n')


class StatType:
    playerInfo, statistics, playerWeekly, weather, injury = range(5)

    def __init__(self):
        pass
