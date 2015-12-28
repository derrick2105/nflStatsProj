# StatType is a helper class that acts like an enum. Each variable represents a type of statistic that the NFLStatsProvider module can fetch.
class StatType:
    playerInfo, statistics, playerWeekly, weather, injury = range(5)