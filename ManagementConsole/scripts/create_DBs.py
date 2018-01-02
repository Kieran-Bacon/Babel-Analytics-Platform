#!/usr/bin/python

import sqlite3
import hashlib
import uuid

#Create Session Database.

conn = sqlite3.connect("../data/sessions.db");
c = conn.cursor()

c.execute("DROP TABLE sessions")
c.execute(" create table sessions (session_id char(128) UNIQUE NOT NULL, atime timestamp NOT NULL default current_timestamp,data text);")
#save changes
conn.commit();
#close connection
conn.close();

# Create Site Database.

conn = sqlite3.connect("../data/site.db");

c = conn.cursor();

#Drop previous tables if database already exists
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
for table in tables:
	tab_name = table[0]
	c.execute('DROP TABLE %s' % tab_name)


# ------------------- End database create ------------------- #

#######################################
###		Access Management Tables	###
#######################################

#users
c.execute("CREATE TABLE users\
		 ( id INTEGER PRIMARY KEY\
		 , username text\
		 , salt text\
		 , password text\
		 , firstname text\
		 , lastname text\
		 , email text\
		 , access_token text\
		 , avatar text\
		 )")


#grp_membership
c.execute("CREATE TABLE grp_membership\
		 ( gid int\
		 , id int\
		 )")

#groups
c.execute("CREATE TABLE groups\
		 ( gid INTEGER PRIMARY KEY\
		 , groupname text\
		 , description text\
		 )")

#grp_act_lkp
c.execute("CREATE TABLE grp_act_lkp\
		 ( gid int\
		 , aid int\
		 )")


#activities
c.execute("CREATE TABLE activities\
		 ( aid INTEGER PRIMARY KEY\
		 , displayname text\
		 , description text\
		 , auth_code text\
		 , auth_level int\
		 )")


#######################################
###		Server Management Tables	###
#######################################

#servers
#A candidate key formed from the machine address and the port number are to be used.
c.execute("CREATE TABLE servers\
		 ( srv_id INTEGER PRIMARY KEY\
		 , eid INTEGER\
		 , display_name text NOT NULL\
		 , description text\
		 , machine_address text NOT NULL\
		 , a_port_num INTEGER NOT NULL\
		 , m_port_num INTEGER NOT NULL\
		 , ssh_port_num INTEGER NOT NULL\
		 , ssh_username text\
		 , ssh_password text\
		 , ssh_key_address text\
		 )")

#services
c.execute("CREATE TABLE services\
		 ( sgid INTEGER PRIMARY KEY\
		 , pid INTEGER NOT NULL\
		 , service_name text NOT NULL\
		 , resource_name text NOT NULL\
		 , description text\
		 )")

c.execute("CREATE TABLE services_versions\
		 ( sid INTEGER PRIMARY KEY\
		 , sgid INTERGER NOT NULL\
		 , version INTEGER NOT NULL\
		 , poolsize INTERGER NOT NULL\
		 , language TEXT NOT NULL\
		 , main_script TEXT NOT NULL\
		 , get_html_file TEXT NOT NULL\
		 , get_redirect TEXT NOT NULL\
		 )")

#Link table between services and environments
c.execute("CREATE TABLE service_deployment_lkp\
		 ( eid INTEGER NOT NULL\
		 , sid INTEGER NOT NULL\
		 , status text NOT NULL\
		 )")

#Environment table
c.execute("CREATE TABLE environments\
		 ( eid INTEGER PRIMARY KEY\
		 , name text\
		 , description text\
		 , env_type text\
		 )")

#Environment type
c.execute("CREATE TABLE env_types\
		 ( name text PRIMARY KEY\
		 , description text\
		 , hierarchy int\
		 )")

#Paths
c.execute("CREATE TABLE paths\
		 ( pid INTEGER PRIMARY KEY\
		 , length INTEGER\
		 , name text\
		 , description text\
		 )")

c.execute("CREATE TABLE env_path_lkp\
		 ( pid INTEGER NOT NULL\
		 , eid INTEGER NOT NULL\
		 , position INTEGER NOT NULL\
		 )")

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




# ------------------- End database create ------------------- #

#######################################
###			Static Data				###
#######################################
#Description:	Initialise the static data required by the management console


#add default user (required for creating new users dynamically)
salt = uuid.uuid4().hex;
m = hashlib.sha256(salt +"admin1").hexdigest();
txt_ins = [salt,m];
c.execute("INSERT INTO users VALUES (NULL, 'admin', ?, ?, 'Admin', 'Admin', 'support@plato-analytics.com', 'Pioneer1234', '/static/images/users/admin/avatar-professional-m.png')",txt_ins)
salt = uuid.uuid4().hex;
m = hashlib.sha256(salt +"Pioneer1234").hexdigest();
txt_ins = [salt,m];
c.execute("INSERT INTO users VALUES (NULL, 'bammins',?,?,'Kieran','Bacon', 'kieran.bacon@outlook.com', 'Pioneer1234', '/static/images/users/admin/avatar-professional-m.png')", txt_ins)
#Define environment types
env_type_data = [
	["DEV", "Environments of this type should be used to build and unit test new analytics services",4],
	["TEST", "Environments of this type should be dedicated to testing teams for all forms of testing and quality control",3],
	["STAGING", "Environments of this type are you used for staging changes ahead of promotion to live.",2],
	["LIVE","Environments of this type are used to deploy analytics services for integration with live systems.",1]
]

for env in env_type_data:
	c.execute('INSERT INTO env_types VALUES (?, ?,?)',env)

#save changes
conn.commit();

#close connection
conn.close();
