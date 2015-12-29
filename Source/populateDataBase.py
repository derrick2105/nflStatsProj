#!/usr/bin/python
import json
from common import StatType
from StatisticsProvider import NFLStatsProvider as provider
from DBMaint import DBMaint
class populateNFLDB():
	def __init__(self):
		self.DB = DBMaint()
		self.provider = provider()
	def populateAll(self):
	
		### TODO: Add try catch blocks 
		# Add all of the non player spacific information. 
		self.populateSeasons()
		self.populateTeams()
		self.populateGames()
		self.populateStats()
		self.populateWeather()
				
		# Add each player, their statsistics, and their injury report. 
		# Currently only adds the latest injury report.
		self.populatePlayers()
		self.populatePlayerStats()
		self.populateInjuryReport()


	def populatePlayers(self):
		# Get stats JSON file
		results =  json.loads(self.provider.getData(StatType.playerInfo))['players']
		
		# build statement
		statement = "insert IGNORE into Players (playerID, firstName, lastName, position) values "
		insertTuples = []
		for value in results:
			tuple = '(' + str(value['id']) + ',"' + str(value['firstName']) + '","' 
			tuple = tuple + str(value['lastName']) + '","' + str(value['position']) + '")'
			insertTuples.append(tuple)
		tuplesString = ','.join(insertTuples)
		statement += tuplesString
		
		# Execute Statement
		self.DB.executeStatement(statement)
		
		# return the results
		return self.DB.getResults()
		
	def populateStats(self):
		# Get stats JSON file
		result =  json.loads(self.provider.getData(StatType.statistics))['stats']
		
		# build statement
		statement = "insert IGNORE into Statistics (statID, name) values "
		insertTuples = []
		for value in result:
			insertTuples.append('(' + str(value['id']) + ",'" + str(value['shortName']) + "')")
		tuplesString = ','.join(insertTuples)
		statement += tuplesString

		# Execute Statement
		self.DB.executeStatement(statement)
		
		# return the results
		return self.DB.getResults()
		
	def populateGames(self):
		return
	def populateInjuryReport(self):
		return
	def populatePlayerStats(self):
		return
		
	def populateTeams(self):
		# Get stats JSON file
		results =  json.loads(self.provider.getData(StatType.playerInfo))['players']
		# build statement
		statement = "insert IGNORE into Teams (teamID, name) values "
		insertTuples = []
		for value in results:
			if str(value['teamAbbr']) == '':
				continue
			else:
				tuple = "('" + str(value['teamAbbr']) + "','filler')" 
				insertTuples.append(tuple)
		tuplesString = ','.join(insertTuples)
		statement += tuplesString
		
		# Execute Statement
		self.DB.executeStatement(statement)
		
		# return the results
		return self.DB.getResults()
	def populateSeasons(self):
		return
	def populateWeather(self):
		return
	def populateDB(self, statement):
		return
	

if __name__ == '__main__':
	populator = populateNFLDB()
	populator.populateTeams()
