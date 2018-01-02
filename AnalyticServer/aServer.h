#ifndef ASERVER_H
#define	ASERVER_H

#include "Server.h"

class aServer: public Server {
public:
    
    /**
     * Sets the toggle parameters pointers as to allow communication between
     * the two servers during operation.
     * @param r - int toggle for running and accepting requests.
     * @param l - int toggle for informing that all start up log messages are
     * finished.
     */
    aServer( int *r, int *l ):
    runToggle( r ), logToggle( l ){}
    
    /**
     * Start listening to requests through the port.
     */
    void start();
    
private:
    
    /**
     * Process the input request and evaluate its intentions before formulating
     * a response object.
     * @param sockFd - socket request is received on.
     */
    void processConnection(int sockFd);
    
    int *runToggle;
    int *logToggle;
};

#endif	/* ASERVER_H */

