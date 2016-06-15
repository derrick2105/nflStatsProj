# StatType is a helper class that acts like an enum. Each variable represents a
# type of statistic that the NFLStatsProvider module can fetch.


class StatType:
    playerInfo, statistics, playerWeekly, weather, injury = range(5)

    def __init__(self):
        pass


# A simple log function that just appends to a log file
def log(message, outfile='./log.txt'):
    with open(outfile, 'a') as f:
        f.write(message)
