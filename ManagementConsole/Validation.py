import web
from DatabaseHandler import DatabaseHandler as db

class Server_Form:
	def POST(self):

		input = web.input( machine_address="NULL", a_port="NULL", m_port="NULL", ssh_port="NULL" )
		response = "{"

		if input.machine_address == "NULL":
			return '{ "a_port":"false", "m_port":"false", "ssh_port":"false" }'
		else:
			if input.a_port != "NULL":
				data = [ input.machine_address ] + [input.a_port]*3
				count = db().execute( "Validation", 0, data )[0][0]

				if count == 0:
					response += '"a_port":"true",'
				else:
					response += '"a_port":"false",'
			else:
				response += '"a_port":"false",'

			if (input.m_port != "NULL" ):
				data = [ input.machine_address ] + [input.m_port]*3
				count = db().execute( "Validation", 0, data )[0][0]

				if count == 0:
					response += '"m_port":"true",'
				else:
					response += '"m_port":"false",'
			else:
				response += '"m_port":"false",'

			if (input.ssh_port != "NULL" ):
				data = [ input.machine_address ] + [input.ssh_port]*3
				count = db().execute( "Validation", 0, data )[0][0]

				if count == 0:
					response += '"ssh_port":"true"'
				else:
					response += '"ssh_port":"false"'
			else:
				response += '"ssh_port":"false"'

		return response + "}"