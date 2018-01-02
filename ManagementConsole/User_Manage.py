import web
import sqlite3
import HelperFunctions as help

render = web.template.render('templates')

class Manage_Users:
	def GET(self):
		help.check_access()
		conn = sqlite3.connect('./data/site.db', isolation_level=None)
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		c.execute("SELECT * FROM users")

		usr_data = c.fetchall()

		return help.renderPage( 'Manage Users', render.manage_users( usr_data ) )