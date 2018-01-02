#ifndef MAINCLASS_H
#define	MAINCLASS_H

#define SOCK_ERRORS  // we will use verbose socket errors

#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <thread>
#include <istream>
#include <fstream> 
#include <map>

#include <libconfig.h++>

#include "sisocks.h"
#include "Rconnection.h"
#include "httpRequest.h"
#include "httpResponse.h"
#include "ServiceDefinition.h"
#include "Engine.h"
#include "AppPool.h"
#include "log1.h"
#include "Datahandler.h"

using namespace libconfig;


/**
 * MainClass contains and controls all resources within the program.
 * After initialising resources (like the RAppPools for all services) it beings 
 * to suspend computation to listen and receive http requests. Each request
 * triggers the program to generate a new thread, so that the main thread can
 * resume listening while the request is handled.  
 */
class Server {
protected:
    int socket_FD, client_length;
    serverParameters *server_param; /* Pointer to server information */
    sockaddr_in server_address, client_address; /* Socket and port ids */
    
    
public:
    /**
     * Deallocate the pointer.
     */
    ~Server(){ server_param = NULL ; }
    
    /**
     * Initialise the server on a parameters specified.
     * @param server info - Structure containing relative server information. 
     * @return status - Indicating if the process was a success.
     */
    int initialiseSocket( serverParameters* );
};

#endif	/* MAINCLASS_H */

