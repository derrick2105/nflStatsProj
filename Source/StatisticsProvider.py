#!/usr/bin/python
import urllib2
from Common import StatType

######
# Add Error handling and interface with a url config file. 


class NFLStatsProvider:
    def __init__(self):
        self.url = None

    def get_data(self, data_type=StatType.playerInfo, week=1, season=2015):
        week = str(week)
        season = str(season)
        if data_type == StatType.playerInfo:
            return self.request("http://api.fantasy.nfl.com/v1/players"
                                "/researchinfo?season=" + season + "&week=" +
                                week + "&count=3000&format=json")
        elif data_type == StatType.statistics:
            return self.request("http://api.fantasy.nfl.com/"
                                "v1/game/stats?format=json")
        elif data_type == StatType.weather:
            return self.request("http://www.fantasyfootballnerd.com/"
                                "service/weather/xml/n4j9tv9n5env/")
        elif data_type == StatType.injury:
            return self.request("http://www.fantasyfootballnerd.com/"
                                "service/injuries/xml/n4j9tv9n5env/" +
                                week + "/")
        elif data_type == StatType.playerWeekly:
            return self.request("http://api.fantasy.nfl.com/v1/players"
                                "/stats?StatName=weekStats&season=" +
                                season + "&week=" + week + "&format=json")

    @staticmethod
    def request(url):
        return urllib2.urlopen(url).read()

if __name__ == '__main__':
    statsProvider = NFLStatsProvider()
    stats = statsProvider.get_data()
    print stats
