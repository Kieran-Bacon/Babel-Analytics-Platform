def main( a, b, c ):
	if( a < b and b < c ):
		return str(b) + " is within the range of " + str(a) + "-" + str(c)
	else :
		global program_status
		program_status = 400
		return str(b) + " is not inside the range!"
