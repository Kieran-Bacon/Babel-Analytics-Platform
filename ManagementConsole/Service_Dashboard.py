import web
import sqlite3
import HelperFunctions as help

render = web.template.render('templates')

class Service_Dashboard:
	def GET(self, resource):
		help.check_access()
		return help.renderPage( "Live Service", render.service_view( resource ) )
