#!/usr/bin/python
import urllib2
import Utilities
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
    """
       NFL Stats Provider wrapper class.
    """
    def __init__(self):
        self.url = None

    def get_data(self, data_type=Utilities.StatType.playerInfo, week=1,
                 season=2015, player_id=0):
        """

        :param data_type:
        :param week:
        :param season:
        :param player_id:
        :return:
        """
        week = str(week)
        season = str(season)

        if data_type == Utilities.StatType.playerInfo:
            return self._request("http://api.fantasy.nfl.com/v1/players"
                                 "/researchinfo?season=" + season + "&week=" +
                                 week + "&count=5000&format=json")
        elif data_type == Utilities.StatType.statistics:
            return self._request("http://api.fantasy.nfl.com/"
                                 "v1/game/stats?format=json")
        elif data_type == Utilities.StatType.weather:
            return self._request("http://www.fantasyfootballnerd.com/"
                                 "service/weather/json/n4j9tv9n5env/")
        elif data_type == Utilities.StatType.injury:
            return self._request("http://api.fantasy.nfl.com/v1/players/"
                                 "details?playerId=" + str(player_id) +
                                 "&format=json")
        elif data_type == Utilities.StatType.playerWeekly:
            return self._request("http://api.fantasy.nfl.com/v1/players"
                                 "/stats?statType=weekStats&season=" +
                                 season + "&week=" + week + "&format=json")
        elif data_type == Utilities.StatType.games:
            return self._request("http://www.fantasyfootballnerd.com/service/"
                                 "schedule/json/n4j9tv9n5env/")
        elif data_type == Utilities.StatType.teams:
            return self._request(("http://www.fantasyfootballnerd.com/service/"
                                  "nfl-teams/json/n4j9tv9n5env/"))
        elif data_type == Utilities.StatType.byes:
            return self._request(("http://www.fantasyfootballnerd.com/service/"
                                  "byes/json/n4j9tv9n5env/"))

    @staticmethod
    def _request(url):
        try:
            req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
            return json.loads(urllib2.urlopen(req).read())

        except urllib2.HTTPError, e:
            Utilities.log(e.msg, Utilities.stat_provider_log)
            if e.args != ():
                Utilities.log("Args: " + str(e.args),
                              Utilities.stat_provider_log)
            return None

        except ValueError, e:
            Utilities.log_exception(e, Utilities.stat_provider_log)
            if e.args != ():
                Utilities.log("Args: " + str(e.args),
                              Utilities.stat_provider_log)
            return None
