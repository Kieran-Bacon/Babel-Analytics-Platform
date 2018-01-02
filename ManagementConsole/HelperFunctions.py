import web
import sqlite3

render = web.template.render('templates')

def strVersion( number ):
	output = ""
	for i in range(len( str(number) )):
		output += str(number)[i] + "."
	output = output[:-1]
	return output

def convert_lang( language ):
	return {
		'.py': 'PYTHON',
		'.r' : 'R',
		'.sas': 'SAS',
		'.exe': 'EXE',
		'NULL': 'NULL'
	}.get( language, "error")

def filename( name ):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	return (''.join( c for c in name if c in valid_chars)).encode('ascii','ignore')

def append_user_alerts( type, title, content):
	session = web.ctx.session
	newAlert = [type, title, content]
	session.alerts.append( newAlert )

def clear_user_alerts():
	session = web.ctx.session
	session.alerts = []


def check_access( permission = "*" ):
	session = web.ctx.session
	check = session.get('loggedin',False)
	lock = session.get('locked', '')

	if check and lock == '':
		return check
	elif lock != '':
		raise web.seeother('/lockscreen.html')
	else:
		raise web.seeother('/login.html')

def renderPage( pageTitle, pageHTML ):
	session = web.ctx.session

	db = sqlite3.connect('./data/site.db')
	db.row_factory = sqlite3.Row
	c = db.cursor()

	c.execute("SELECT s.sgid, s.service_name FROM services_versions ser, services s, service_deployment_lkp sdl, environments env WHERE s.sgid = ser.sgid AND ser.sid = sdl.sid AND sdl.eid = env.eid AND env.env_type = 'LIVE' GROUP BY ser.sgid")
	Services = c.fetchall()

	c.execute("SELECT res.location FROM webpages wp, web_resources_lkp wrl, resources res WHERE wp.page_name = 'nav_menu' AND wp.wid = wrl.wid AND wrl.rid = res.rid AND res.type = 'css'")
	CSS = c.fetchall()
	c.execute("SELECT res.location FROM webpages wp, web_resources_lkp wrl, resources res WHERE wp.page_name = ? AND wp.wid = wrl.wid AND wrl.rid = res.rid AND res.type = 'css'",(pageTitle,))
	PageCSS = c.fetchall()
	for C in CSS:
		PageCSS.append( C )

	c.execute("SELECT res.location FROM webpages wp, web_resources_lkp wrl, resources res WHERE wp.page_name = ? AND wp.wid = wrl.wid AND wrl.rid = res.rid AND res.type = 'js'",(pageTitle,))
	JS = c.fetchall()
	c.execute("SELECT res.location FROM webpages wp, web_resources_lkp wrl, resources res WHERE wp.page_name = 'nav_menu' AND wp.wid = wrl.wid AND wrl.rid = res.rid AND res.type = 'js'")
	PageJS = c.fetchall()
	for J in JS:
		PageJS.append( J )

	db.close()

	page_info = [pageTitle, session.first_name, session.last_name , session.avatar]
	out_html = render.nav_menu( page_info , pageHTML, Services, PageCSS, PageJS, session.alerts )
	clear_user_alerts()
	web.header('Content-Type','text/html; charset=utf-8', unique=True)
	return(out_html)
