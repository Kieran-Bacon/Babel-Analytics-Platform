import web
import hashlib
import sqlite3
import HelperFunctions as help
from os import stat, mkdir

render = web.template.render('templates')


#######################################
###				login				###
#######################################

#Description: 	This class renders the login page and handles login requests.

class Login:
	def GET(self):
		return render.login([])
	def POST(self):
		session = web.ctx.session
		conn = sqlite3.connect('./data/site.db')
		conn.row_factory = sqlite3.Row
		c = conn.cursor()
		input = web.input()

		if input.username is None or input.password is None:
			raise web.badrequest()

		c.execute("SELECT * FROM users WHERE username = ?", (input.username,))
		r = c.fetchone()

		if r is None:
			return render.login([['error','Whoops!','Your username password combination is incorrect']])

		# r = [ id, username, salt, password, first name, last name, email, status, avatar]

		m = hashlib.sha256(r['salt'] + input.password)

		if m.hexdigest() == r['password']:
			session.loggedin = True
			session.locked = ''
			session.id = r['id']
			session.username = input.username
			session.access_token = r['access_token']
			session.first_name = r['firstname']
			session.last_name = r['lastname']
			session.alerts = []
			session.avatar = r['avatar']

			raise web.seeother("/dashboard.html")
		else:
			return render.login([['error','Whoops!','Your username password combination is incorrect']])

#Description: 	This class handles logout requests.

class Logout:
	def GET(self):
		session = web.ctx.session
		if session.get('loggedin',False):
			#conn = sqlite3.connect('./data/session.db')
			#conn.row_factory = sqlite3.Row
			#c = conn.cursor()
			#c.execute("DELETE FROM sessions WHERE session_id = ?",(session.get_id(),))
			#conn.commit()
			session.loggedin = False
		raise web.seeother("/login.html")

#######################################
###				lock				###
#######################################

class Lock:
	def GET(self):
		session = web.ctx.session
		return render.lockscreen( session.first_name + ' ' + session.last_name, [] )
	def POST(self):
		session = web.ctx.session
		input = web.input( url="NULL" )
		if input.url == "NULL":
			raise web.badrequest()

		session.locked = input.url

		return render.lockscreen( session.first_name + ' ' + session.last_name, [] )

class Unlock:
	def POST(self):
		session = web.ctx.session
		input = web.input( password="NULL" )
		if input.password == "NULL":
			raise web.badrequest()

		conn = sqlite3.connect('./data/site.db')
		conn.row_factory = sqlite3.Row
		c = conn.cursor()

		c.execute("SELECT * FROM users WHERE username = ?", (session.username,))
		r = c.fetchone()

		if r is None:
			return render.login([['error','Whoops!','Sessions information is missing.']])

		# r = [ id, username, salt, password, first name, last name, email, status]

		m = hashlib.sha256(r['salt'] + input.password)

		if m.hexdigest() == r['password']:
			temp = session.locked
			session.locked = ''
			
			raise web.seeother(temp)
		else:
			return render.lockscreen( session.first_name + ' ' + session.last_name, [['error','Whoops!','Your password is incorrect']])

class File_Upload:
	def POST(self):
		
		help.check_access()
		session = web.ctx.session
		usr = session.get("username",False)
		if usr:
			filedir = "./temp/uploads/" + usr + "/"
			try:
				stat(filedir)
			except:
				mkdir(filedir)
		else:
			raise web.forbidden()

		x = web.input(file={})

		if 'file' in x:
			filepath=x.file.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
			filename=filepath.split('/')[-1] # splits by / and chooses the last part (the filename with extension)
			fout = open(filedir + filename,'w') # creates the file where the uploaded file should be stored
			fout.write(x.file.file.read()) # writes the uploaded file to the newly created file.
			fout.close() # closes the file, upload complete.

		return 200

class File_Download:
	def GET(self, filepath ):
		help.check_access()
		if filepath[:2] != './':
			filepath = './' + filepath
		return open( filepath, "r").read()
