#ifndef MSERVER_H
#define	MSERVER_H

#include <stdio.h>

#include "Server.h"
#include "BinStructures.h"

class mServer: public Server {
    /*
     *This class represents a the management section of the analytics server and
     * handles instructions relating to the operation of the server.
    */
    
public:
    mServer( int *r, int *l, const std::string& ll):
    runToggle( r ), logToggle( l ){ logLevel =  new std::string( ll ); }
    
    //Start the management server
    void start();
    
    int flushServiceDirectory();
    
    

private:
    int *runToggle;
    int *logToggle;
    std::string *logLevel;
    bin *garbageCollector;
    
    static void binMan( bin*, int* );
    
    void processConnection( int socket );
    


    int ACTIVATE(const std::string& resource);
    int DEACTIVATE(const std::string& resource);
    std::string STATUS(const std::string& resource);
    std::string ADDRESS(const std::string& resource);
    std::string  LS();
    int NEW( const std::string& payload );
    int UPDATE( const std::string& target, const std::string& configAddress );
    int DELETE( const std::string& resource );

    
    
};

#endif	/* MSERVER_H */

