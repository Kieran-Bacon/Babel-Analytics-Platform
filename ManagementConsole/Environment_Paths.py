import web
from DatabaseHandler import DatabaseHandler as db
import HelperFunctions as help

render = web.template.render('templates')

class Environment_Details:
	
	def GET( self, pid ):

		dev = [name for row in db().executeLiteral( "SELECT env.name FROM environments env, env_path_lkp epl WHERE env.eid = epl.eid AND env.env_type = 'DEV' AND epl.pid = ?", [pid]) for name in row]
		test = [name for row in db().executeLiteral( "SELECT env.name FROM environments env, env_path_lkp epl WHERE env.eid = epl.eid AND env.env_type = 'TEST' AND epl.pid = ?", [pid]) for name in row]
		stage = [name for row in db().executeLiteral( "SELECT env.name FROM environments env, env_path_lkp epl WHERE env.eid = epl.eid AND env.env_type = 'STAGING' AND epl.pid = ?", [pid]) for name in row]
		live = [name for row in db().executeLiteral( "SELECT env.name FROM environments env, env_path_lkp epl WHERE env.eid = epl.eid AND env.env_type = 'LIVE' AND epl.pid = ?", [pid]) for name in row]

		selected = [ dev, test, stage, live]

		ns_dev = [name for row in db().executeLiteral( "SELECT name FROM environments WHERE env_type = 'DEV'", []) for name in row if not name in dev ]
		ns_test = [name for row in db().executeLiteral( "SELECT name FROM environments WHERE env_type = 'TEST'", []) for name in row if not name in test]
		ns_stage = [name for row in db().executeLiteral( "SELECT name FROM environments WHERE env_type = 'STAGING'", []) for name in row if not name in stage]
		ns_live = [name for row in db().executeLiteral( "SELECT name FROM environments WHERE env_type = 'LIVE'", []) for name in row if not name in live]

		not_selected = [ ns_dev, ns_test, ns_stage, ns_live ]

		path_info = [0, "Quick Production"]

		return help.renderPage( "Environment Paths", render.environment_details( path_info, not_selected, selected ))

class Environment_Paths:
	def GET(self):

		all_paths = db().executeLiteral( "SELECT * FROM paths", [])

		path_info = []
		types = ['DEV','TEST','STAGING','LIVE']

		for path in all_paths:
			temp = [path[0], path[2], path[1]]
			for t in types:
				temp.append( (db().executeLiteral( "SELECT COUNT(*) FROM environments env, env_path_lkp epl WHERE epl.pid = ? AND env.env_type = ? AND epl.eid = env.eid", [path[0], t])[0])[0] )
			path_info.append( temp )


		return help.renderPage( "Environment Paths", render.environment_paths( path_info ) )