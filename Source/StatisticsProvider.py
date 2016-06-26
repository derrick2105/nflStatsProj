#!/usr/bin/python
import urllib2
import Common
import json

######
# TODO
# 1. Find a better weather api that has historical data
# 2. Possibly replace the injury report api if it is not useful
######

######
# This is a wrapper class for statistics api calls. Replace the urls to
# change the data source.
######


class NFLStatsProvider:
    def __init__(self):
        self.url = None

    def get_data(self, data_type=Common.StatType.playerInfo, week=1,
                 season=2015, player_id=0):
        week = str(week)
        season = str(season)

        if data_type == Common.StatType.playerInfo:
            return self.request("http://api.fantasy.nfl.com/v1/players"
                                "/researchinfo?season=" + season + "&week=" +
                                week + "&count=3000&format=json")
        elif data_type == Common.StatType.statistics:
            return self.request("http://api.fantasy.nfl.com/"
                                "v1/game/stats?format=json")
        elif data_type == Common.StatType.weather:
            return self.request("http://www.fantasyfootballnerd.com/"
                                "service/weather/json/n4j9tv9n5env/")
        elif data_type == Common.StatType.injury:
            return self.request("http://api.fantasy.nfl.com/v1/players/"
                                "details?playerId=" + str(player_id) +
                                "&format=json")
        elif data_type == Common.StatType.playerWeekly:
            return self.request("http://api.fantasy.nfl.com/v1/players"
                                "/stats?statType=weekStats&season=" +
                                season + "&week=" + week + "&format=json")
        elif data_type == Common.StatType.games:
            return self.request("http://www.fantasyfootballnerd.com/service/"
                                "schedule/json/n4j9tv9n5env/")
        elif data_type == Common.StatType.teams:
            return self.request(("http://www.fantasyfootballnerd.com/service/"
                                 "nfl-teams/json/n4j9tv9n5env/"))

    @staticmethod
    def request(url):
        try:
            req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
            return json.loads(urllib2.urlopen(req).read())

        except urllib2.HTTPError, e:
            Common.log(e.msg, Common.stat_provider_log)
            if e.args != ():
                Common.log("Args: " + str(e.args), Common.stat_provider_log)
            return None

        except ValueError, e:
            Common.log_exception(e, Common.stat_provider_log)
            if e.args != ():
                Common.log("Args: " + str(e.args), Common.stat_provider_log)
            return None

if __name__ == '__main__':
    statsProvider = NFLStatsProvider()
    raw_data = statsProvider.get_data(data_type=Common.StatType.games)
    if raw_data is not None:
        results = json.loads(raw_data)
        print results
