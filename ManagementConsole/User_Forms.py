import web
import sqlite3
import HelperFunctions as help

render = web.template.render('templates')

class Add_User:
	def GET(self):
		raise web.forbidden()
	def POST(self):
		#input: username, first_name, last_name, email, password, cpassword, groups

		input = web.input()
		conn = sqlite3.connect('./data/site.db', isolation_level=None)
		c = conn.cursor()

		inputValues = [input.username, input.first_name, input.last_name, input.email, input.password]
		inputCheck = [True, True, True, True, True]

		c.execute("SELECT * FROM users WHERE username = ?", (input.username,))
		r = c.fetchone()

		if r is not None:
			inputCheck[0] = False

		if input.username == '':
			inputCheck[0] = False

		if input.first_name == '':
			inputCheck[1] = False

		if input.last_name == '':
			inputCheck[2] = False

		if input.email == '':
			inputCheck[3] = False
		#validate other inputs

		#if any input is incorrect, return the page with the warnings for that thing.
		if not all(inputCheck):
			raise web.forbidden()

		salt = uuid.uuid4().hex
		m = hashlib.sha256(salt + input.password)
		data = [input.username, salt, m.hexdigest(), input.first_name, input.last_name, input.email];

		c.execute("INSERT INTO users VALUES (NULL,?,?,?,?,?,?,1)", data)
		conn.commit()

		raise web.seeother("/index.html")