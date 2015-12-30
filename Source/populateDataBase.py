#!/usr/bin/python
import json
from common import StatType
from StatisticsProvider import NFLStatsProvider as provider
from DBMaint import DBMaint


####
# TODO: 
#		1. Add error catching to each call.
#		2. write the games, injury, stats, and Weather methods
###
class populateNFLDB():
	def __init__(self):
		self.DB = DBMaint()
		self.provider = provider()

	def __del__(self):
		del self.DB
		del self.provider

	def populateAll(self):
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
		statement1 = "insert IGNORE into Players (playerId, firstName, lastName, position) values "
		insertTuples1 = []
		statement2 = "insert IGNORE into PlayerTeam(playerId, teamId) values "
		insertTuples2 = []
		for value in results:
			tup = '(' + str(value['id']) + ',"' + str(value['firstName']) + '","' 
			tup = tup + str(value['lastName']) + '","' + str(value['position']) + '")'
			insertTuples1.append(tup)
			if str(value['teamAbbr']) == '':
				continue
			else:
				insertTuples2.append( '(' + str(value['id']) + ',"' + str(value['teamAbbr']) + '")')
		statement1 += ','.join(insertTuples1)
		statement2 += ','.join(insertTuples2)
		
		# Execute Statements
		self.populateDB(statement1)
		self.populateDB(statement2)
		
	def populateStats(self):
		# Get stats JSON file
		result =  json.loads(self.provider.getData(StatType.statistics))['stats']
		
		# build statement
		statement = "insert IGNORE into Statistics (statID, name) values "
		insertTuples = []
		for value in result:
			insertTuples.append('(' + str(value['id']) + ",'" + str(value['name']) + "')")
		tuplesString = ','.join(insertTuples)
		statement += tuplesString

		# Execute Statement
		self.populateDB(statement)
		
	
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
				tup = "('" + str(value['teamAbbr']) + "','filler')" 
				insertTuples.append(tup)
		statement += ','.join(insertTuples)
		
		# Execute Statement
		self.populateDB(statement)
		
	def populateSeasons(self):
		# Build Statement
		Seasonid = 0
		statement = "insert ignore into Season (SeasonId, week, year) values "
		insertTuples = []
		# 2010-2015 Seasons
		for i in range(2010,2016):
			# Weeks 1-17
			for j in range(1,18):
				tup = '(' + str(Seasonid + j) + ',' + str(j) + ',' + str(i) + ')'
				insertTuples.append(tup)
			Seasonid += 17
		statement += ','.join(insertTuples)
		
		# Execute Statement
		self.populateDB(statement)

	def populateWeather(self):
		return

	def populateDB(self, statement):
		# Add logic to verify input maybe?
		self.DB.executeStatement(statement)
	

if __name__ == '__main__':
	populator = populateNFLDB()
	populator.populateSeasons()
