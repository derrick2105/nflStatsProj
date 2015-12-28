import urllib2
from Common import StatType

######
# Add Error handling and interface with a url config file. 

class NFLStatsProvider():
	def getData(self, type = StatType.playerInfo, week = 1, season = 2015, option = None):
		week = str(week)
		season = str(season)
		if type == StatType.playerInfo:
			return self.requestContent("http://api.fantasy.nfl.com/v1/players/researchinfo?season=" + season + "&week=" + week + "&count=2000&format=json")
		elif type == StatType.statistics:
			return self.requestContent("http://api.fantasy.nfl.com/v1/game/stats?format=json")
		elif type == StatType.weather:
			return self.requestContent("http://www.fantasyfootballnerd.com/service/weather/xml/n4j9tv9n5env/")
		elif type == StatType.injury:
			return self.requestContent("http://www.fantasyfootballnerd.com/service/injuries/xml/n4j9tv9n5env/" + week + "/")
		elif type == StatType.playerWeekly:
			return self.requestContent("http://api.fantasy.nfl.com/v1/players/stats?statType=weekStats&season=" + season + "&week=" + week + "&format=json")
	def requestContent(self, url):
		return urllib2.urlopen(url).read()
	
if __name__ == '__main__':
	statsProvider = NFLStatsProvider()
	stats = statsProvider.getData()
	print stats