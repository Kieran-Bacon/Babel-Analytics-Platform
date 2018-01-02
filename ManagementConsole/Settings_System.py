import web
import HelperFunctions as help
from DatabaseHandler import DatabaseHandler as db

render = web.template.render('templates')

class System_Settings:
	def GET(self):
		return "Hello"