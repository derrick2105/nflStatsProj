#!/usr/bin/python
import MySQLdb


######
# This is a wrapper class that is designed to abstract away Database specifics.
class DBMaint():
	def __init__(self):
		self.conn = None

	def __del__(self):
		self.closeDBConnection()
	
	def openDBConnection(self, config = './config'):
		# open file maybe xml
		# read connection settings
		# open connection
		# conn = MySQLdb.connect(host='192.168.1.73',user='pythonUser', passwd='pythonPassword', db='BITCOIN_PRICE')
		if self.conn is not None:
			self.closeDBConnection()

		IP = '192.168.1.10'
		UserName = 'pythonUser'
		password = 'pythonPassword'
		dataBase = 'NFLStats1'
		self.conn = MySQLdb.connect(host=IP,user=UserName, passwd=password, db=dataBase)

	def closeDBConnection (self):
		if self.conn:
			self.conn.close()
			self.conn = None
		if self.cursor:
			self.cursor = None

	def getCursor(self):
		#Open a connection if the dataBase is closed. 
		if self.conn is None:
			self.openDBConnection()

		self.cursor = self.conn.cursor()

	def executeStatement(self, statement):
		if self.cursor is None:
			self.getCursor()
		self.cursor.execute(statement)

	def getResults(self):
		ret = []
		for x in range(int(self.cursor.rowcount)):
			ret.append(self.cursor.fetchone())
		return ret
