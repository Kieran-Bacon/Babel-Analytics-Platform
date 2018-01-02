import web
import sqlite3
import HelperFunctions as help

render = web.template.render('templates')

class User_View:
	def GET(self):
		return help.renderPage( "Profile", render.user_view() )