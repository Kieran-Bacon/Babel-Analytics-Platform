#!/usr/bin/python

import string
import web
import sqlite3
import hashlib
import uuid
import os
from os import listdir
from os.path import isfile, join
import json
import pylibconfig2 as cfg


# Custom python modules

#from analyticsserver import AnalyticsServer

from Dashboard import Dashboard, AJAX_dashboard
from Access import Login, Logout, Lock, Unlock, File_Upload, File_Download

from Environment_Manage import Environments
from Environment_Forms import Add_Environment, Edit_Environment, Delete_Environment
from Environment_Details import Environment_Details, AJAX_Service_Requests, AJAX_Service_CPU
from Environment_Actions import Activate_Service, Deactivate_Service

from Path_Manage import Manage_Paths
from Path_Forms import Add_Path, Edit_Path, Delete_Path
from Path_Details import Path_Details, AJAX_Path_Update

from Service_Dashboard import Service_Dashboard
from Service_Manage import Manage_Services
from Service_Details import Service_Details, AJAX_Version_Data
from Service_Forms import Add_Service, Edit_Service, Delete_Service, Add_Version, Delete_Version # Edit_Version
from Service_Actions import Promote, Demote

from Server_Manage import Manage_Servers, AJAX_manage_servers
from Server_Forms import Add_Server, Edit_Server, Delete_Server
from Server_Details import Server_Details

from User_Manage import Manage_Users
from User_View import User_View
from User_Forms import Add_User

from Settings_User import User_Settings
from Settings_System import System_Settings

from Validation import Server_Form



from Ajax import AJAX_service_details, AJAX_deploy_service, AJAX_activate_service, AJAX_deactivate_service



import HelperFunctions as help
from DatabaseHandler import DatabaseHandler

# End of Custom python modules

web.config.debug = False

urls = (
	"/login.*", "Login",
	"/logout.py", "Logout",
	"/lockscreen.*","Lock",
	"/unlock.py","Unlock",
	"/dashboard.html", "Dashboard",
	"/file_upload.html","File_Upload",
	"/download/(.+)", "File_Download",

	"/AJAX/dashboard.*", "AJAX_dashboard",
	"/AJAX/service_details_(.+)", "AJAX_Version_Data",
	"/AJAX/add_server.*", "Server_Form",
	"/AJAX/deploy_service.*", "AJAX_deploy_service",
	"/AJAX/activate_service.*", "Activate_Service",
	"/AJAX/deactivate_service.*", "Deactivate_Service",
	"/AJAX/file_upload.*", "AJAX_file_upload",

	"/environments.*", "Environments",
	"/environment_details_(.+)", "Environment_Details",

	"/environment_form_0", "Add_Environment",
	"/environment_form_(.+)", "Edit_Environment",
	"/environment_delete_(.+)", "Delete_Environment",
	"/environment_details_(.+)", "Environment_Details",
	"/AJAX/SerReq/environment_details_(.+)", "AJAX_Service_Requests",
	"/AJAX/SerCPU/environment_details_(.+)", "AJAX_Service_CPU",
	"/environments.html", "Manage_Environments",

	"/path_form_0", "Add_Path",
	"/path_form_(.+)", "Edit_Path",
	"/path_delete_(.+)", "Delete_Path",
	"/path_details_(.+)","Path_Details",
	"/AJAX/path_details_(.+)", "AJAX_Path_Update",
	"/paths.html", "Manage_Paths",

	"/manage_services.*", "Manage_Services",
	"/service_dashboard_(.+)", "Service_Dashboard",
	"/service_details_(.+)", "Service_Details",
	"/add_service.*","Add_Service",
	"/edit_service_(.+)", "Edit_Service",
	"/delete_service_(.+)", "Delete_Service",
	"/add_version_(.+)", "Add_Version",
	#"/edit_version_(.+)", "Edit_Version",
	"/delete_version_(.+)", "Delete_Version",

	"/promotion_(.+)", "Promote",
	"/demotion_(.+)", "Demote",
	
	"/manage_servers.*", "Manage_Servers",
	"/AJAX_manage_servers_(.+)","AJAX_manage_servers",
	"/add_server.*","Add_Server",
	"/edit_server_(.+)","Edit_Server",
	"/server_details_(.+)", "Server_Details",
	"/delete_server_(.+)", "Delete_Server",

	"/manage_users.*","Manage_Users",
	"/user_view.*","User_View",
	"/add_user.py","Add_User",
	
	
	"/deactivate_service.*", "deactivate_service",
	"/deploy_service.*", "deploy_service",
	"/check_servicename.py", "check_servicename",
	"/server_status.*", "server_status",

	"/system_settings.html", "System_Settings",
	"/user_settings.html", "User_Settings",
	
    ".*", "static_handler"
)

app = web.application(urls, locals())
render = web.template.render('templates')

#Define the database to store web session data
db = web.database(dbn='sqlite',	db='data/sessions.db')
store = web.session.DBStore(db,'sessions')
session = web.session.Session(app, store)

def session_hook():
	web.ctx.session = session

app.add_processor(web.loadhook(session_hook))
DatabaseHandler().load( "./sql/" )


#Set the document root for ?????
doc_root = os.getcwd()


#######################################
###			static_handler			###
#######################################

#Description: 	This class handles access to all static content
#				and makes use of 'X-LIGHTTPD-senf-file'

class static_handler:
	def GET(self):
		
		path = web.ctx.path

		if path == "/":
			if session.get('loggedin',False):
				raise web.seeother("/dashboard.html")
			else:
				raise web.seeother("/login.html")

		protectedExtensions = [".html",".htm",".py"]

		for extention in protectedExtensions:
			if path.endswith( extention ):
				help.check_access()
				web.header("X-LIGHTTPD-send-file",doc_root + path)
				return "Access granted"
		
		resourcesExtensions = [".css",".js",".jpg",".png",".ico",".woff",".woff2",".ttf",".r",".py",".txt"]
		for extention in resourcesExtensions:
			if path.endswith( extention ):
				web.header("X-LIGHTTPD-send-file",doc_root + path)
				return "Access granted"

		raise web.forbidden()

if __name__ == "__main__":
    app.run()