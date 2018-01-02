# HTTP message tests

import sys
import socket
from AnalyticsServerInterface import Server

from itertools import product
from string import ascii_lowercase
keywords = map(''.join, product(ascii_lowercase, repeat=3))

if len(sys.argv) != 6:
	print( "Insufficent test arguments, please provide: address, aPort, mPort, username, token")
	exit()

Analytics = Server( sys.argv[1], int(sys.argv[2]) )
Management = Server( sys.argv[1], int(sys.argv[3]) )

test_passed = 0
test_failed = 0

############################
print( "Test one: Valid http request" )
permissions = { "Username": sys.argv[4], "Access-Token":sys.argv[5] }
resp = Management.send( "OPTIONS", "/", permissions )
if resp == "FAILED" or resp[0] != "200":
	print( "FAILED" )
	test_failed += 1
else:
	print( "PASSED" )
	test_passed += 1

############################
print( "Test two: Garbage Request" )
garbage = "k jonapnsncjansnaidcm ajosn oianiccniu89hub2 jn asujncind"
send_buffer = garbage.encode()
sockethandler = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
sockethandler.settimeout( 5 )

try:
	sockethandler.connect( ( sys.argv[1], int(sys.argv[2]) ) )
	sockethandler.send( send_buffer )
	sockethandler.settimeout(None)
	response = sockethandler.recv(4096).decode()
	sockethandler.close()

	status = response[ response.index(' ')+1: response.index(' ')+4]
	body = response[ response.index('\n\n')+2:]

	if status != "200":
		print( "PASSED" )
		test_passed += 1
	else:
		raise Exception

except Exception as e:
	sockethandler.close()
	print("FAILED")
	test_failed += 1

##################################

print( "Test three: Malformed Request header" )
Malformed = { "Username": sys.argv[4], "Access-Token":sys.argv[5], "Content-Length":"-1" }
resp = Management.send( "TRACE", "/", Malformed )
if resp == "FAILED" or resp[0] == "200":
	print( "FAILED" )
	test_failed += 1
else:
	print( "PASSED" )
	test_passed += 1

###################################

print( "Test Four: Gigantic Requests" )
LargeHeader = { "Username": sys.argv[4], "Access-Token":sys.argv[5] }
keywords = map(''.join, product(ascii_lowercase, repeat=4))
for word in keywords:
	LargeHeader[word] = "TEST INPUT"

resp = Management.send( "TRACE", "/", LargeHeader, timeout=11 )
if resp == "FAILED" or resp[0] != "408":
	print("FAILED")
	test_failed += 1
else:
	print("PASSED")
	test_passed += 1

print(str( test_passed + test_failed ) + " tests run, " + str(test_passed) + " passed, " + str(test_failed) + " failed.")