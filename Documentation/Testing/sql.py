import sqlite3
import time 

def main():
	global empNames
	global cusNames

	result = empNames + cusNames

	return str( result )

def setup():
	global empNames
	global cusNames

	empNames, cusNames = [],[]

	database = sqlite3.connect('./chinook.db')
	database.row_factory = sqlite3.Row
	cursor = database.cursor()

	cursor.execute( "SELECT count(*) FROM employees", [])
	num = cursor.fetchone()[0]

	for i in range( int(num)*10 ):
		cursor.execute( "SELECT * FROM employees", [] )
		response = cursor.fetchall()
		for a in response:
			empNames.append( [i] + list(a) )

	cursor.execute( "SELECT count(*) FROM customers", [])
	num = cursor.fetchone()[0]

	for i in range( int(num)*10 ):
		cursor.execute( "SELECT * FROM customers", [] )
		response = cursor.fetchall()
		for a in response:
			cusNames.append( [i] + list(a) )

	#Commit and close connection to the site.
	database.commit()
	database.close()

if __name__ == "__main__":
	start = time.time()
	setup()
	what = time.time()
	main()
	print( 'time: ', time.time() - start, time.time()-what )
