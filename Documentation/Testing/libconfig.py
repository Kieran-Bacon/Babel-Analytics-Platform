import pylibconfig2 as cfg

def create( filepath, service ):

	string = 'version = "' + service[0] + '";\n\n'
	string += 'serviceInfo = {\n'
	string += '\tworkingDirectory = "' + service[1] + '";\n'
	string += '\tmainScript = "' +service[2] + '";\n'
	string += '\tlanguage = "' + service[3] + '";\n'
	string += '\tpoolSize = ' + str(service[4])+ ';\n'
	string += '\tHTTP_Status = ' + str( service[5] )+ ';\n'
	string += '\tGET_HTML = "' + service[6] + '";\n'
	string += '};'

	newFile = open( filename, "w")
	newFile.write(string)
	newFile.close()

	print string

#Adding Configuration File

newList = ["1.0.0.1", "./pRange/","inRange.py","PYTHON",2,303,"www.google.com"]

create( newList )
