import web
import HelperFunctions as help
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class Environments:

	def GET( self ):
		list_of_environments = db().executeLiteral( "SELECT * FROM environments", [])
		return help.renderPage("Environments", render.environments( list_of_environments ))