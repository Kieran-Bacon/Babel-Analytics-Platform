import time 

def main( value ):
	values = []
	for i in range( 1, int(value)):
		if value % i == 0:
			values.append([i, value/i])
	return values

if __name__ == "__main__":
	start = time.time()
	print( main( 425868 ) )
	print( "time: ", time.time() - start )
	