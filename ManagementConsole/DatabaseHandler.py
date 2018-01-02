from os import listdir
from os.path import isfile, join
import sqlite3

class DatabaseHandler:

	allQueries = {}

	def load( self, location ):

		#For every file in the location of the sql commands.
		for file in listdir( location ):
			#Read the file and convert the contents to a sting without new lines or tabs.
			file_reader = open( join(location,file), 'r').read()
			file_reader = (file_reader.replace("\n", " ")).replace("\t","")

			#Temp list of queries for this particular file.
			queries = []

			#Each command is followed by a single star, this allows for quick disection of
			# the file contents.

			while( "#" in file_reader ):
				queries.append( file_reader[0:file_reader.index("#")])
				file_reader = file_reader[file_reader.index("#")+2:]

			#The queries for a file are then added to the global dictionary.

			self.allQueries[file] = queries

	""" Executes a sql command found in the static dictionary and
		returns its result to the client.
		Returns: List of all rows the command captures. """
	def execute(self, classOrigin, index, sqlVariables):

		#Extracting the command from the static Dictionary
		sqlCommand = (self.allQueries[classOrigin])[index]

		return self.executeLiteral( sqlCommand, sqlVariables)

	def executeID( self, classOrigin, index, sqlVariables):
		#Extracting the command from the static Dictionary
		sqlCommand = (self.allQueries[classOrigin])[index]

		return self.execute_return_ID( sqlCommand, sqlVariables)

	def execute_return_ID( self, sqlCommand, sqlVariables ):

		#Creating a connection to the site database. 
		database = sqlite3.connect('./data/site.db')
		database.row_factory = sqlite3.Row
		cursor = database.cursor()

		#execute Command against the database and capture.
		cursor.execute( sqlCommand, sqlVariables )
		temp = cursor.lastrowid

		#Commit and close connection to the site.
		database.commit()
		database.close()

		return temp

	def executeLiteral( self, sqlCommand, sqlVariables ):

		#Creating a connection to the site database. 
		database = sqlite3.connect('./data/site.db')
		database.row_factory = sqlite3.Row
		cursor = database.cursor()

		#execute Command against the database and capture.
		cursor.execute( sqlCommand, sqlVariables )
		response = cursor.fetchall()

		#Commit and close connection to the site.
		database.commit()
		database.close()

		return response


	def printwork( self ):
		print self.allQueries
