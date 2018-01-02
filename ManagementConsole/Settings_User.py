import web
import HelperFunctions as help
from DatabaseHandler import DatabaseHandler as db
from Dashboard import Dashboard

render = web.template.render('templates')

class User_Settings:
	def GET(self):
		return "hello"