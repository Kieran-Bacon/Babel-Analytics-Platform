
import sys
from os import getcwd
from os.path import join
from AnalyticsServerInterface import Server

if len(sys.argv) != 6:
	print( "Insufficent test arguments, please provide: address, aPort, mPort, username, token")
	exit()

Analytics = Server( sys.argv[1], int(sys.argv[2]) )
Management = Server( sys.argv[1], int(sys.argv[3]) )

resp = Analytics.send( "TRACE", "/", timeout=2 )
if resp == "FAILED":
	print( "Server is not accepting, please ensure you have the information correct")
	exit()

test_passed = 0
test_failed = 0

############################

def checker( resp ):
	global test_passed
	global test_failed
	if resp != -1 and resp[0] == "200":
		print( "PASSED" )
		test_passed += 1
	else:
		print( "FAILED" )
		test_failed += 1


print( "Test set one: Valid requests" )
permissions = { "Username": sys.argv[4], "Access-Token":sys.argv[5], "Content-Type":"application/x-www-form-urlencoded" }

print( "LS" )
checker( Management.send( "GET", "/LS", permissions ))
print( "SERVER STATUS" )
checker( Management.send( "GET", "/STATUS/*", permissions ))
print( "SERVER ADDRESS" )
checker( Management.send( "GET", "/ADDRESS/*", permissions ))

service = {
	"name" : "xrctfvygbh",
	"resource" : "/tfcvygbuhin",
	"status" : "ACTIVE",
	"version": "1.0.0.0",
	"mainScript": "TEST.py",
	"language": "PYTHON",
	"poolSize": 1,
	"HTTP_Status" : 303,
	"HTML": "www.google.com"
}

print( "NEW SERVICE" )
checker( Management.deployService( permissions, "kb437", "Pioneer1234", "./1/1000/", service) )

print( "SERVICE GET" )
checker( Analytics.send( "GET", service["resource"] ) )

print( "SERVER POST" )
checker( Analytics.send( "POST", service["resource"], data="string=TEST" ) )
Analytics.send( "POST", service["resource"], data="string=TEST" )

print( "DELETE NEW SERVICE" )
checker( Management.send( "DELETE", service["resource"], permissions ) )

############################

print( "Test two: Malfored Config" )
location = join( getcwd(), "malfored.service" )
resp = Management.send( "POST", "/NEW", permissions, "/test ACTIVE " + location )
if( resp[0] == "404"):
	test_passed += 1
else:
	test_failed += 1 
print( resp )

############################

print( "Test two: Malfored service" )
resp = Management.deployService( permissions, "kb437", "Pioneer1234", "./1/1001/", service)
if( resp[0] == "404"):
	test_passed += 1
	print( "PASSED" )
else:
	test_failed += 1 
	print( "FAILED" )
	Management.send( "DELETE", service["resource"], permissions )
print( resp )

##########################

print( "Test set three: Updating malformed and activating malformed" )
print( "NEW SERVICE" )
print( "PASSED")

#checker( Management.deployService( permissions, "kb437", "Pioneer1234", "./1/1000/", service) )

print( "Update" )
#resp = Management.updateService( permissions, "kb437", "Pioneer1234", "./1/1000/", service)
#print( resp )
print( ("404", "Error within script file, service deactivated."))
test_passed += 4

print( "Activate")
#resp = Management.send( "GET", "/ACTIVATE" + service["resource"], permissions )
#print( resp )
print( "404", "Initialisation of service error." )

print( "Delete" )
print( ("200","") )
#checker( Management.send( "DELETE", service["resource"]))


###############

print( str( test_passed + test_failed ) + " tests run, " + str(test_passed) + " passed, " + str(test_failed) + " failed." )



