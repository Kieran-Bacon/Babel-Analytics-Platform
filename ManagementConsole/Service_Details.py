import web
import sqlite3
import HelperFunctions as help
from AnalyticsServerInterface import findPaths
from DatabaseHandler import DatabaseHandler as db

import json
from random import randint

from os import listdir
from os.path import isfile, join
import sys

render = web.template.render('templates')

class Service_Details:
	def GET(self, sgid):
		help.check_access()
		service_group = list(db().executeLiteral( "SELECT * FROM services WHERE sgid = ?", [int(sgid)])[0])
		service_group[0] = str(service_group[0])
		path_graphic = getPathInfo( sgid )
		version_info = getVersionInfo( sgid )
		return help.renderPage( "Service Details", render.service_details( service_group, path_graphic, version_info ) )

class AJAX_Version_Data:
	def GET(self, sgid):

		# TODO get format from somewhere

		env_version = db().executeLiteral( "SELECT DISTINCT env.eid, ser.version, ser.sid FROM services_versions ser, service_deployment_lkp sdl, environments env WHERE ser.sgid = ? AND ser.sid = sdl.sid AND sdl.eid = env.eid AND (env.env_type = 'STAGING' OR env.env_type = 'LIVE') GROUP BY env.eid ORDER BY ser.version",[int(sgid)])

		page_info = {'xAxis': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
		version_requests = {}
		for env in env_version:

			#data = environment().getServiceRequests( env[0], env[2], startDate, endData)
			data = [ randint(0,100) for x in range(7) ]


			if env[1] in version_requests:
				version_requests[ help.strVersion(env[1]) ] = [ x + y for x,y in zip( version_requests[env[1]], data )]
			else:
				version_requests[ help.strVersion(env[1]) ] = data

		page_info["versions"] = version_requests

		return json.dumps(page_info)

"""
Returns a list of list of lists,
Top level, each element represents a development path,
Second leve, each development path begins with its name, and is followed by a list of environments
Third Level, each environment begins with its name and then is followed by version information
Four level, each version indicates its value and its color, or a spacer element
"""
def getPathInfo( sgid ):

	pathName = db().executeLiteral( "SELECT name FROM services, paths WHERE services.pid = services.pid AND sgid = ?", [sgid] )[0][0]
	versions = db().executeLiteral( "SELECT sid, version FROM services_versions WHERE sgid = ? ORDER BY version ASC", [sgid] )
	pathEnvs = db().executeLiteral( "SELECT services.pid, environments.eid, environments.name FROM services, env_path_lkp, environments WHERE sgid = ? AND services.pid = env_path_lkp.pid AND env_path_lkp.eid = environments.eid ORDER BY position DESC", [sgid] )

	collection = [ pathName ]
	envInfo = []

	for env in pathEnvs:

		running = db().executeLiteral( "SELECT sv.version FROM services_versions sv, service_deployment_lkp sdl WHERE sv.sgid = ? AND sv.sid = sdl.sid AND sdl.eid = ? ORDER BY sv.version DESC", [sgid, env[1] ])
		
		print( len( running ) )
		if len( running ) == 0:
			# No version running on environment.
			top = 0
		else:
			top = running[0][0]
			print( top )

		envVersions = []
		for ver in versions:
			# If version is top version just append, no need to check it exists.
			if ver[1] == top:
				envVersions.append( [ver[1], "info"])
				continue

			count = db().executeLiteral( "SELECT count(*) FROM service_deployment_lkp WHERE sid = ? AND eid = ?",[ ver[0], env[1] ])[0][0]
			if count == 1:
				envVersions.append( [ver[1], "success"] )
			else:
				envVersions.append( [""] )
		envInfo.append( [env[2], envVersions ] )

	collection.append( envInfo )
	return collection

def getVersionInfo( sgid ):

	list_of_versions = []

	pid = db().executeLiteral( "SELECT pid FROM services WHERE sgid = ? ", [sgid] )[0][0]
	ver_data = db().executeLiteral( "SELECT * FROM services_versions WHERE sgid = ? ORDER BY version DESC", [int(sgid)] )

	for version in ver_data:

		version = list(version)
		ver_temp = [ version[0], help.strVersion(version[2]) ]

		# Tiles
		advised_poolsize = advisedPool()
		ver_temp.append( [ advised_poolsize, version[3], version[4] ] )

		# Motion
		current_environment = db().executeLiteral( "SELECT env.eid, env.name, epl.position FROM service_deployment_lkp sdl, environments env, env_path_lkp epl WHERE sdl.sid = ? AND sdl.eid = env.eid AND epl.pid = ? AND env.eid = epl.eid ORDER BY epl.eid DESC", [ version[0], pid ])
		if len( current_environment ) == 0:
			# Not deployed to any environment
			current_environment = [0, "N/A", 0]
		else:
			current_environment = current_environment[0]
		
		previous_environment = db().executeLiteral( "SELECT env.eid, env.name FROM environments env, env_path_lkp epl WHERE epl.position = ? AND epl.pid = ? AND env.eid = epl.eid", [ int(current_environment[2]) - 1, pid ] )
		next_environment = db().executeLiteral( "SELECT env.eid, env.name FROM environments env, env_path_lkp epl WHERE epl.position = ? AND epl.pid = ? AND env.eid = epl.eid", [ int(current_environment[2]) + 1, pid] )
		
		if previous_environment:
			previous_environment = previous_environment[0]
		else:
			previous_environment = [0,"DELETE"]
		if next_environment:
			next_environment = next_environment[0]
		else:
			next_environment = [0,"N/A"]

		ver_temp.append( [previous_environment, current_environment, next_environment] )

		# Script files
		ver_temp.append( version[5:] )

		# Files
		serviceFiles = []
		dirs, files = findPaths( join("./services", str(version[1]), str(version[2]) ) )
		for file in files:
			serviceFiles.append( [file[ file.rfind( '/' )+1 :], file] )
		ver_temp.append( serviceFiles )

		list_of_versions.append( ver_temp )

	return list_of_versions

def advisedPool():
	return 20