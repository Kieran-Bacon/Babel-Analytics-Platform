import sqlite3
db = sqlite3.connect("../data/site.db")
c = db.cursor()

tables = ["webpages", "web_resources_lkp", "resources"]
for table in tables:
	c.execute('DROP TABLE %s' % table)


c.execute("CREATE TABLE webpages\
		 ( wid NUMBER PRIMARY KEY\
		 , page_name text\
		 )")

c.execute("CREATE TABLE web_resources_lkp\
		 ( wid NUMBER\
		 , rid NUMBER\
		 )")

c.execute("CREATE TABLE resources	\
		 ( rid NUMBER PRIMARY KEY\
		 , type text\
		 , location text\
		 )")

pages = ["nav_menu",
		 "Dashboard",
		 "Environment Paths",
		 "Path Details",
		 "Service Details",
		 "Manage Servers",
		 "Add Service",
		 "Add Server",
		 "Add Version",
		 "Edit Version",
		 "Add Environment",
		 "Edit Environment",
		 "Environment Details"
		]

resources = [[["nav_menu"], "css", "./static/vendors/bootstrap/dist/css/bootstrap.min.css"],
			 [["nav_menu"], "css", "./static/vendors/font-awesome/css/font-awesome.min.css"],
			 [["nav_menu"], "css", "./static/vendors/pnotify/dist/pnotify.css"],
    		 [["nav_menu"], "css", "./static/vendors/pnotify/dist/pnotify.buttons.css"],
    		 [["nav_menu"], "css", "./static/vendors/pnotify/dist/pnotify.nonblock.css"],
    		 [["nav_menu"], "css", "./static/build/css/custom.min.css"],
    		 [["Add Environment", "Edit Environment"], "css", "./static/vendors/select2/dist/css/select2.min.css"],
    		 [["Add Environment", "Edit Environment"], "js", "./static/vendors/select2/dist/js/select2.full.min.js"],
    		 [["Add Environment", "Edit Environment"], "js", "./static/js/environment_form.js"],
    		 [["Dashboard","Environment Details"], "js", "./static/js/theme.js"],
    		 [["Environment Details"], "js", "./static/js/environment_details.js"],

			 [["Add Service","Add Server", "Add Version", "Edit Version"],"css","./static/vendors/switchery/dist/switchery.min.css"],
			 [["Add Service","Add Server", "Add Version", "Edit Version"], "js","./static/vendors/switchery/dist/switchery.min.js"],


			 [["Add Service", "Add Version", "Edit Version"],"css","./static/vendors/dropzone/dist/min/dropzone.min.css"],
			 [["Add Service"], "js","./static/vendors/dropzone/dist/dropzone.js"],

			 [["nav_menu"], "js", "./static/vendors/bootstrap/dist/js/bootstrap.min.js"],


			 [["nav_menu"], "js", "./static/vendors/pnotify/dist/pnotify.js"],
			 [["nav_menu"], "js", "./static/vendors/pnotify/dist/pnotify.buttons.js"],
			 [["nav_menu"], "js", "./static/vendors/pnotify/dist/pnotify.nonblock.js"],

			 [["Add Service", "Add Version", "Edit Version"],"css","./static/vendors/iCheck/skins/flat/green.css"],

			 #[["Environment Details"],"css", "./static/vendors/bootstrap-progressbar/css/bootstrap-progressbar-3.3.4.min.css"],
			 [["Environment Details"],"js", "./static/vendors/raphael/raphael.min.js"],
			 [["Environment Details"],"js", "./static/vendors/morris.js/morris.min.js"],

			 
			 [["Dashboard","Service Details", "Environment Details"], "js", "./static/vendors/echarts/dist/echarts.min.js"],
			 [["Dashboard","Service Details", "Environment Details"], "js", "./static/vendors/echarts/map/js/world.js"],
			 [["Dashboard","Service Details"], "js", "./static/vendors/bootstrap-progressbar/bootstrap-progressbar.min.js"],
			 
			 [["Service Details"],"js","./static/vendors/select2/dist/js/select2.full.min.js"],
			 [["Service Details"],"js","./static/js/service_details.js"],

			 

			 [["Add Service", "Add Version", "Edit Version"],"js","./static/vendors/iCheck/icheck.min.js"],
			 [["Add Service", "Add Version", "Edit Version"],"js","./static/vendors/jQuery-Smart-Wizard/js/jquery.smartWizard.js"],

			 

			 [[],"js","./static/js/validator.js"],
			 [[],"js","./static/vendors/fastclick/lib/fastclick.js"],
			 [[],"js","./static/vendors/nprogress/nprogress.js"],

			 [["nav_menu"], "js", "./static/js/nav_menu.js"],
			 [["Dashboard"], "js", "./static/js/dashboard.js"],
			 [["Add Server"],"js","./static/js/add_server.js"],
			 [["Manage Servers"],"js","./static/js/server_manage.js"],

			 [["Add Service", "Add Version", "Edit Version"], "css", "./static/vendors/normalize-css/normalize.css"],
			 [["Add Service", "Add Version", "Edit Version"], "css", "./static/vendors/ion.rangeSlider/css/ion.rangeSlider.css"],
			 [["Add Service", "Add Version", "Edit Version"], "css", "./static/vendors/ion.rangeSlider/css/ion.rangeSlider.skinFlat.css"],
			 
			 [["Add Service", "Add Version", "Edit Version"],"js","./static/vendors/dropzone/dist/min/dropzone.min.js"],

			 [["Add Service", "Add Version", "Edit Version"],"js","./static/vendors/ion.rangeSlider/js/ion.rangeSlider.min.js"],

			 [["Add Service", "Add Version", "Edit Version"],"js","./static/js/add_service.js"],

			 [["Path Details"], "js", "./static/vendors/Sortable/Sortable.js"],
			 [["Path Details"], "js", "./static/js/env_path.js"],
			 [["nav_menu"], "js", "./static/build/js/custom.js"]
			 
			]

pageID = 1
resourceID = 1
resdict = {}


for pageName in pages:
	c.execute('INSERT INTO webpages VALUES ( ?, ?)',(pageID, pageName,))
	for resource in resources:
		if pageName in resource[0]:
			keys = resdict.keys()
			if resource[2] in keys:
				c.execute('INSERT INTO  web_resources_lkp VALUES (?, ?)',(pageID,resdict[resource[2]],))
			else:
				c.execute('INSERT INTO  web_resources_lkp VALUES (?, ?)',(pageID,resourceID,))
				c.execute('INSERT INTO resources VALUES (?, ?, ?)', (resourceID, resource[1], resource[2],))

				resdict[ resource[2] ] = resourceID
				resourceID = resourceID + 1
	pageID = pageID + 1




c.execute("SELECT * FROM webpages")
pages = c.fetchall()
print "Pages"
for page in pages:
	print page

c.execute("SELECT * FROM resources")
resources = c.fetchall()
print "\nResources"
for res in resources:
	print res

c.execute("SELECT * FROM web_resources_lkp")
lkp = c.fetchall()
print "\nLookup"
for l in lkp:
	print l

db.commit()
db.close()
