import socket
from os import mkdir, rmdir, listdir
from os.path import isfile, isdir, join 
import paramiko

class Server:
	def __init__( self, host, port, pReturn=False ):

		self.host = host
		self.port = port
		self.pReturn = pReturn

	def send( self, method, resource, headers={}, data=""):

		message = method + " " + resource + " HTTP/1.1" + "\r\n"
		for key in headers.keys():
			message += key+": "+headers[key] + "\r\n"
		if ( len(data) != 0 ):
			message += "Content-Length: " + str( len(data) ) + "\r\n"
		message += "\r\n" + data

		send_buffer = message.encode()
		sockethandler = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

		try:
			sockethandler.connect( (self.host, self.port) )
			sockethandler.send( send_buffer )
		except Exception as e:
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

	def createService( self, permissions, username, password, service ):
		resp = self.send( "GET", "/ADDRESS/*", permissions );
		if resp == "FAILED":
			return "Error on connection - Failed to create new service"

		serverConfig, servicesDirectory, logDirectory = resp[1].split(' ')

		uploader = paramiko.SSHClent()
		uploader.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

		uploader.connect( self.host, username=username, password=password )
		stream = uploader.open_stfp()

		dirs, paths = findPaths( service["directory"] )
		target = join( serviceDirectory, service["resource"])

		stream.mkdir( target )

		# Create a dir for every dir removing the initial absolute aspect.
		for dir in dirs:
			stream.mkdir( join( target, dir[len(service["directory"]):] ) )

		# Put all the files into their correct places.
		for path in paths:
			stream.put( path, join( target, path[ len(service["directory"]) :] ))

		stream.close()
		uploader.close()

		msg = service["resource"] + " " + service["status"] + " " + join( target, service["config"])
		self.send( "POST", "/NEW", headers=permissions, data=msg )

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


p = { "Username":"bammins", "Access-Token": "Pioneer1234" }
h = { "Content-Type":"application/x-www-form-urlencoded" }
d = "int=10&int=20&int=30"
data = "/duplicated ACTIVE /home/bammins/services/duplicated/etc/Add.cfg"

"""
manage = Server( "127.0.0.1", 5665 )
AS = Server( "127.0.0.1", 7980 )


#manage.send( "GET", "/DEACTIVATE/range", p )
#manage.send( "GET", "/ACTIVATE/range", p)
AS.send( "POST", "/range", h, d)
AS.send( "POST", "/range", h, d)
AS.send( "POST", "/range", h, d)
"""
"""
manage.send( "OPTIONS", "/", p)
manage.send( "GET", "/LS", p)
manage.send( "GET", "/ADDRESS/*", p)
manage.send( "GET", "/STATUS/*", p )
manage.send( "GET", "/ADDRESS/Analytics/Adding-Service", p)

AS.send( "GET", "/Analytics/Adding-Service" )

print( "----------------Activate and Deactive------------------")
AS.send( "POST", "/Analytics/Adding-Service", h, d )

manage.send( "GET", "/DEACTIVATE/Analytics/Adding-Service", p)

AS.send( "GET", "/Analytics/Adding-Service" )
AS.send( "POST", "/Analytics/Adding-Service", h, d )

manage.send( "GET", "/ACTIVATE/Analytics/Adding-Service", p)

AS.send( "GET", "/Analytics/Adding-Service" )
AS.send( "POST", "/Analytics/Adding-Service", h, d )

print("------------------------------------------------")

manage.send( "POST", "/NEW", p, data)

manage.send( "GET", "/LS", p)

AS.send( "POST", "/duplicated", h, d)

manage.send( "DELETE", "/duplicated", p)

manage.send( "GET", "/LS", p)

AS.send( "POST", "/duplicated", h, d)
"""
