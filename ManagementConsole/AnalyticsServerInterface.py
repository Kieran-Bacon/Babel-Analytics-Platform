import socket
from os import mkdir, rmdir, listdir, remove
from os.path import isfile, isdir, join 
import paramiko

class Server:
	def __init__( self, host, port, pReturn=False ):

		self.host = host
		self.port = port
		self.pReturn = pReturn

	def send( self, method, resource, headers={}, data="", timeout=30):

		message = method + " " + resource + " HTTP/1.1" + "\r\n"
		for key in headers.keys():
			message += key+": "+headers[key] + "\r\n"
		if ( len(data) != 0 ):
			message += "Content-Length: " + str( len(data) ) + "\r\n"
		message += "\r\n" + data

		send_buffer = message.encode()
		sockethandler = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		sockethandler.settimeout( timeout )

		try:
			sockethandler.connect( (self.host, self.port) )
			sockethandler.send( send_buffer )
			sockethandler.settimeout(None)
		except Exception as e:
			if self.pReturn:
				print( e )
			return "FAILED"

		response = sockethandler.recv(4096).decode()
		sockethandler.close()

		if self.pReturn:
			try:
				status = response[ response.index( ' ' ) + 1: response.index( ' ' ) + 4]
				body = response[ response.index( '\n\n' )+2:]
				print status + " " + body
			except:
				print response
		else:
			try:
				status = response[ response.index(' ')+1: response.index(' ')+4]
				body = response[ response.index('\n\n')+2:]
				return ( status, body)
			except:
				return ( response )

	def retrieveMaster(self, permissions, srv_id, username, password ):

		resp = self.send( "GET", "/ADDRESS/*", permissions )
		if resp == "FAILED":
			return "Error on connection - Failed to create new service"

		target = join( "./configs", str(srv_id) )

		serverConfig, servicesDirectory, logDirectory = resp[1].split(' ')

		downloader = paramiko.SSHClient()
		downloader.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		try:
			downloader.connect( self.host, username=username, password=password )
		except:
			print( username, password )
			downloader.close()
			return -1

		# Delete the current config for this server if it exists.
		try:
			remove( target )
		except:
			pass

		stream = downloader.open_sftp()
		stream.get( serverConfig, target )

		stream.close()
		downloader.close()
		return 0

	def createService( self, permissions, username, password, directory, service ):
		"""
			Permissions - the headers for any message to be sent to server.
			username - ssh accepted Username
			password - ssh accepted password for username
			directory - The directory of the service that is being uploaded.
			service - dictionary of information to construct the service config. 
		"""

		# Ask the server for the directory information, split into the different locations.
		resp = self.send( "GET", "/ADDRESS/*", permissions );
		if resp == "FAILED":
			return -1
		serverConfig, servicesDirectory, logDirectory = resp[1].split(' ')

		print( resp )
		print( username, password )
		print( directory )

		# Constructe the new target directory path.
		target = join( servicesDirectory, service["name"] )

		print( target )

		# Construct the service configuration.
		serCon = 'version = "' + str(service["version"]) + '";\n\n'
		serCon += 'serviceInfo = {\n'
		serCon += '\tworkingDirectory = "' + target + '";\n'
		serCon += '\tmainScript = "' + service["mainScript"] + '";\n'
		serCon += '\tlanguage = "' + service["language"] + '";\n'
		serCon += '\tpoolSize = ' + str(service["poolSize"])+ ';\n'
		serCon += '\tHTTP_Status = ' + str( service["HTTP_Status"] )+ ';\n'
		serCon += '\tGET_HTML = "' + service["HTML"] + '";\n'
		serCon += '};'

		# Define a name for the config, will be on target machine.
		configName = service["name"] +  ".cfg"

		# Define a local version of the name so that no possible clashes are formed.
		localName = permissions['Username'] + "_" + str(service["version"]) + "_" + configName
		
		# Create the config in the temp space for moving.
		newConfig = join(".", "temp", "configs", localName )
		newFile = open( newConfig , "w")
		newFile.write(serCon)
		newFile.close()

		# Get all the dir information and the path information for the service.
		dirs, paths = findPaths( directory )
		
		# Attempt to open a open a ssh connection to the target machine.
		uploader = paramiko.SSHClient()
		uploader.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		try:
			uploader.connect( self.host, username=username, password=password )
		except AuthenticationException:
			# Delete temp config close attempt and return.
			remove( newConfig )
			uploader.close()
			return -1

		# Indicate that files shall be transfered, make the target directory, my config across.
		stream = uploader.open_sftp()

		try:
			stream.mkdir( target )
		except IOError:
			pass


		stream.put( newConfig, join( target, configName ))

		# Create a dir for every dir removing the local absolute aspect.
		for dir in dirs:
			stream.mkdir( join( target, dir[ dir.rfind( '/' )+1 :] ) )

		# Put all the files into their correct places.
		for path in paths:
			stream.put( path, join( target, path[ path.rfind('/')+1 :] ))

		# Close connnection and remove newly created config.
		stream.close()
		uploader.close()
		remove( newConfig )

		# Notify the server about the new server.
		msg = service["resource"] + " " + service["status"] + " " + join( target, configName )
		resp = self.send( "POST", "/NEW", headers=permissions, data=msg )
		print( "HERE IS THE RESP FROM THE SERVER", resp )
		if resp == "FAILED" or resp[0] != "200":

			print( "GOT HERE" )

			cleanup = paramiko.SSHClient()
			cleanup.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
			try:
				cleanup.connect( self.host, username=username, password=password )
			except AuthenticationException:
				# Delete temp config close attempt and return.
				cleanup.close()
				return -1

			stream = cleanup.open_sftp()
			for file in paths:
				print( file, join( target, path[ path.rfind('/')+1 :] ) )
				stream.remove( join( target, path[ path.rfind('/')+1 :] ) )

			# Need to delete lower folders before higher.
			for folder in dirs[::-1]:
				stream.rmdir( join( target, dir[ dir.rfind( '/' )+1 :] ) )

			try:
				stream.rmdir( target )
			except:
				pass

			stream.close()
			cleanup.close()

		return resp

	def getLogs(self, srv_id, permissions, username, password ):
		resp = self.send( "GET", "/ADDRESS/*", permissions );
		if resp == "FAILED":
			return "Error on connection - Failed to create new service"

		serverConfig, servicesDirectory, logDirectory = resp[1].split(' ')
		target = join( "./logs", str(srv_id) )

		downloader = paramiko.SSHClient()
		downloader.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		try:
			downloader.connect( self.host, username=username, password=password )
		except AuthenticationException:
			downloader.close()
			return -1

		# Try to make the dir, don't if it exists.
		try:
			mkdir( target )
		except:
			pass

		stream = downloader.open_sftp()

		# Get a list of local and server logs
		filenames = stream.listdir( logDirectory )
		local = listdir( target )

		# Remove logs that exist on the server (as they might be editted there)
		for file in [x for x in local if x in filenames ]:
			remove( join( target, file ) )

		# Get all logs
		for file in filenames:
			stream.get( join( logDirectory, file), join( target, file ) )

		stream.close()
		downloader.close()

		return 0

def findPaths( directory ):
	dirs = []
	paths = []
	for element in listdir( directory ):
		path = join( directory, element )
		if isfile( path ):
			paths.append( path )
		if isdir( path ):
			dirs.append( path )
			d, p = findPaths( path )
			dirs = dirs + d
			paths = paths + p
	return (dirs, paths) 