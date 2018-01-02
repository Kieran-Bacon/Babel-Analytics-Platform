import time

def main( input ):
	factorList = []
	for v in range( 1, int(input) ):
		if int(input) % v == 0:
			factorList.append( [v, int(input)/v] )
	return factorList

if __name__ == "__main__":
	startTime = time.time()
	main( 96724316 )
	finishTime = time.time()
	print( "Time taken to complete: " + str( finishTime - startTime ))
