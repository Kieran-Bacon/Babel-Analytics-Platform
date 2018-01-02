#include "mServer.h"

void  mServer::start()
{
    // Start Garbage collector
    garbageCollector = new bin;
    std::thread trashThread( mServer::binMan, garbageCollector, runToggle );
    
    listen(socket_FD, server_param->queueSize);
    
    FILE_LOG( logINFO ) 
        << "Started Management Server - Port: " << server_param->portNum;
    
    while( *logToggle < 10 ){}
    if( *logToggle == 11 ){
        try {
            FILELog::ReportingLevel() = FILELog::FromString( *logLevel );
        } catch(const std::exception& e){
            FILE_LOG(logERROR) << e.what();
        }
    } else {
        FILELog::logLocation() = Datahandler::getLogging()->root_directory;
    }
    
    //Loop to accept inbound connections
    while( *runToggle ){
        int newsockFd = accept(socket_FD, 
                    (sockaddr *) &client_address, (socklen_t *) &client_length);
        if (newsockFd < 0) {
                FILE_LOG(logERROR) <<"Error on accept connection: "
                        << strerror(errno) << ".";
        }
        
        processConnection( newsockFd );
    }
    FILE_LOG( logINFO ) << "Closing Management Server...";
    close(socket_FD);
    trashThread.join();
    FILE_LOG( logINFO ) << "Bin man thread stopped, Management shutdown.";
}

void mServer::processConnection( int socket )
{
    httpRequest http_reqt( socket, Datahandler::getManagement() );
    httpResponse http_resp( socket, Datahandler::getManagement() );
    
    int n = http_reqt.readFromSocket();
    if( n == -1)
    {
        // For Post method, content length corrupted or non existent.
        http_resp.HTTP_Status = 400;
        http_resp << "Malformed request - content length error.";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING )
            << "Management: "
            << http_reqt.version << " " 
            << http_reqt.resource << " Malformed Request.";
        return;
    }
    else if( n == -2 )
    {
        // Message parsing was timed out.
        http_resp.HTTP_Status = 408;
        http_resp << "Connection timeout.";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING )
            << "Management: Received message timed out before parsing completed.";
        return;
    }
    else if( n == -3 )
    {
        // Error during reading, respond and return.
        http_resp.HTTP_Status = 400;
        http_resp << "Error reading HTTP request";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING ) << "HTTP/1.1 " << http_resp.HTTP_Status << " " << http_reqt.resource; 
        return;
    }
    
    // Determine if the user is authorised.
    int validation = Datahandler::validate( http_reqt.requestHeader.Username );
    permissions::level userAuth = 
        Datahandler::authenticate( http_reqt.requestHeader.Access_Token );
    if( validation || userAuth == permissions::DENIED )
    {
        http_resp.HTTP_Status = 403;
        http_resp.writeToSocket();
        close( socket );
        FILE_LOG( Management )
            << HTTP::stringify(http_reqt.method) << " " << http_reqt.resource << " " 
            << http_resp.HTTP_Status << " "
            << "Management Server: Access denied to " 
            << http_reqt.requestHeader.Username << " with access token "
            << http_reqt.requestHeader.Access_Token << ".";
        return;
    }
    
    n = 0;
    size_t delimiter = http_reqt.resource.substr( 1 ).find( '/' );
    std::string action = http_reqt.resource.substr( 1, delimiter );
    std::string target = http_reqt.resource.substr( delimiter + 1 );
    
    switch (http_reqt.method)
    {
        case HTTP::GET:
            // Perform action.
            if( action == "ACTIVATE" )
            {
                n = ACTIVATE( target );
                if( n == 1 ) http_resp << "Malformed service configuration. ";
                if( n == -1) http_resp << "Initialisation of service error. ";
            }
            if( action ==  "DEACTIVATE" )
            { 
              if( userAuth > permissions::LEVELTWO) 
                {n = DEACTIVATE( target );}
              else 
                { n = -10; }
            }
            if( action == "STATUS" ) http_resp << STATUS( target );
            if( action == "ADDRESS" ) http_resp << ADDRESS( target );
            if( action == "LS" ) http_resp << LS();
            
            // Assess if action was successful.
            if( !n ) http_resp.HTTP_Status = 200;
            else{ 
                if( n == -10 )
                { 
                    http_resp.HTTP_Status = 403; 
                    http_resp << "You do not have the credentials to "
                              << "perform this action";
                } else {
                    http_resp.HTTP_Status = 500; http_resp << "FAILURE"; 
                }
            }
            break;

        case HTTP::POST:
            if( http_reqt.resource == "/NEW" )
            { 
                if( userAuth == permissions::ADMIN ) 
                {
                    n = NEW( http_reqt.message_body );
                    if( n == -1 ){
                        http_resp.HTTP_Status = 400;
                        http_resp << "Malformed request.";
                    } else if( n == -2 ){
                        http_resp.HTTP_Status = 403;
                        http_resp << "Resource already exists.";
                    } else if ( n == 11 ){
                        http_resp.HTTP_Status = 400;
                        http_resp << "Service configuration error.";
                    } else if ( n == 9 ){
                        http_resp.HTTP_Status = 400;
                        http_resp << "The program is on an unknown language.";
                    } else if ( n == 8 ){
                        http_resp.HTTP_Status = 400;
                        http_resp << "Program file could not be accessed.";
                    } else if ( n == 7 ) {
                        http_resp.HTTP_Status = 400;
                        http_resp << "Program flagged error during start up.";
                    } else if( n == 8 ){
                        http_resp.HTTP_Status = 400;
                        http_resp << "Main function has not been defined.";
                    } else if( n == 0 ) {
                        http_resp.HTTP_Status = 200;
                        http_resp << "SUCCESS.";
                    } else {
                        http_resp.HTTP_Status = 500;
                        http_resp 
                            << "Unknown error with code:" 
                            << std::to_string(n) << ".";
                    }
                }
            } else 
            {
                http_resp.HTTP_Status = 400;
            }
            break;
        case HTTP::PUT:
            if( userAuth > permissions::LEVELTWO ){
                n = UPDATE( http_reqt.resource, http_reqt.message_body );
                if( !n ){
                    http_resp.HTTP_Status = 200;
                    http_resp << "SUCCESS";
                } else if ( n == 1 ){
                    http_resp.HTTP_Status = 400;
                    http_resp
                        << "FAILED: Error within configuration file, service deactivated.";
                } else if ( n == -1 ) {
                    http_resp.HTTP_Status = 400;
                    http_resp
                        << "FAILED: Error within script file, service deactivated.";
                } else if ( n == -2 ) {
                    http_resp.HTTP_Status = 404;
                }
            } else {
                http_resp.HTTP_Status = 403; 
                http_resp << "You do not have the credentials to "
                          << "perform this action";
            }
        case HTTP::DELETE:
            if( userAuth == permissions::ADMIN ){
                n = DELETE( http_reqt.resource );
                if( !n ) http_resp.HTTP_Status = 200;
                else http_resp.HTTP_Status = 404;
            } else {
                http_resp.HTTP_Status = 403;
                http_resp << "You do not have the credentials to "
                          << "perform this action";
            }
            break;
        case HTTP::TRACE:
            http_resp << http_reqt.message;
            http_resp.HTTP_Status = 200;
            break;
            
        case HTTP::OPTIONS:
            http_resp.HTTP_Status = 200;
            http_resp << "Get Methods:\n"
                << "\t /ACTIVATE/[resource]     - Activate a resource.\n"
                << "\t /DEACTIVATE/[resource]   - Deactivates a resource.\n"
                << "\t /STATUS/*                - Fetch status of the server.\n"
                << "\t /STATUS/[resource]       - Fetch current state of resource.\n"
                << "\t /ADDRESS/*               - Fetch address of the Server configuration, and the address of the service and log directories.\n"
                << "\t /ADDRESS/[resource]      - Fetch the resource's configuration file address.\n"
                << "\t /LS                      - List services (resource names) the server known to the server.\n"
                << "\t /SHUTDOWN                - Gracefully shutdown server.\n"
                
                << "Post Methods: \n"
                << "\t /NEW { resource, status, configAddress } - Create new service on the server.\n"
                    
                << "Put Methods: \n"
                << "\t /[resource] { config address } - Refresh a service by restarting the Application pool with new config\n"
                
                << "Delete Method:\n"
                << "\t /[resource]              - Permanently delete service and its files.\n";
            break;
        default:
            http_resp.HTTP_Status = 405;    //HTTP "Method Not Allowed"
            break;
    }
    
    // Respond to message and close connection.
    http_resp.writeToSocket();
    close(socket);
    
    std::string reason;
    if( http_reqt.resource == "/NEW" || http_resp.HTTP_Status != 200) 
        reason = http_resp.message_body;
    FILE_LOG( Management )
        << HTTP::stringify(http_reqt.method) << " " 
        << http_reqt.requestHeader.Username << " " << http_reqt.resource << " "
        << http_resp.HTTP_Status << " " << reason;
}

int mServer::ACTIVATE( const std::string& resource )
{
    // Get Services structure.
    serviceDirectory *services = Datahandler::getServices();
    
    for (int i=0; i < services->num_defined; i++){
        // Check to see if resource is a service.
        if (resource == services->resourceName[i]){
            
            // If the service isn't active already start it and initialise.
            if( services->applicationPool[i]->getStatus() != POOL::ACTIVE ){
                
                
                
                services->applicationPool[i]->setStatus( POOL::START );
                int n = flushServiceDirectory();
                if( n ){
                    FILE_LOG( logWARNING ) 
                        << "Management Server: Resource " << resource << " has"
                        << "failed to be activated.";
                    return n;
                }
            }
            
            FILE_LOG(logINFO) 
                << "Management Server: Resource \'"
                << resource << "\' has been activate successfully";
            
            return 0;
        }
    }
    
    //specified resource not found
    FILE_LOG(logWARNING) 
        << "Management Console: Unable to activate resource \'"
        << resource 
        << "\'. No services were found matching the specified resource name";
    return -1;
}

int mServer::DEACTIVATE(const std::string& resource)
{
    // Get the services structure.
    serviceDirectory *services = Datahandler::getServices();
    for (int i=0; i < services->num_defined; i++){
        // Check the resource exists.
        if (resource == services->resourceName[i]){
            
            // Check the current status of the engine.
            if( services->applicationPool[i]->getStatus() != POOL::INACTIVE ){
                // Switch the service to stopped and flush the pool clean.
                services->applicationPool[i]->setStatus( POOL::STOP );
                flushServiceDirectory();
            }
            
            FILE_LOG(logINFO) 
                << "Management Server: Resource \'"
                << resource << "\' has been deactivate successfully";
            return 0;
        }
    }
    
    //specified resource not found
    FILE_LOG(logWARNING) 
        << "Management Console: Unable to deactivate resource \'"
        << resource 
        << "\'. No services were found matching the specified resource name";
    return -1;
}

std::string mServer::STATUS(const std::string& resource)
{
    // Resource asking for server status.
    if (resource == "/*"){
        return "Analytics Server: Accepting.";
    }
    
    // Get services structure.
    serviceDirectory *services = Datahandler::getServices();
    
    for (int i = 0; i < services->num_defined; i++){
        if (resource == services->resourceName[i]){
            // Return the status of the Application pool.
            return POOL::stringifyStatus( 
                    services->applicationPool[i]->getStatus() );
        }
    }
    return "No such resource exists.";
}

std::string mServer::ADDRESS(const std::string& resource)
{
    // Get master configuration location.
    if ( resource == "/*"){
        std::string locations = Datahandler::getInstance()->config_Address + " "
                              + Datahandler::getServices()->root_directory + " "
                              + Datahandler::getLogging()->root_directory;
        return locations;
    }
    
    // Get services structure.
    serviceDirectory *services = Datahandler::getServices();
    
    for (int i = 0; i < services->num_defined; i++){
        if (resource == services->resourceName[i]){
            // Return services configuration location.
            return services->configAddress[i];
        }
    }
    return "No such resource exists.";
}

std::string mServer::LS()
{    
    std::string out;
    serviceDirectory *services = Datahandler::getServices();
    
    for (int i = 0; i < services->num_defined; i++)
    {
        out = out 
            + services->resourceName[i] + " " 
            + POOL::stringifyStatus( services->applicationPool[i]->getStatus())
            + "\n";
    }
    
    return out;
}

int mServer::NEW( const std::string& payload )
{
    // Split input into separate sections.
    size_t delimiterCount = std::count( payload.begin(), payload.end(), ' ');
    if( delimiterCount != 2 )  return -1;
    
    size_t DFpos = payload.find( ' ' ), DSpos = payload.find_last_of( ' ' );
    std::string resource = payload.substr( 0, DFpos );
    std::string status = payload.substr( DFpos +1 , DSpos - DFpos -1 );
    std::string config = payload.substr( DSpos + 1 );
    
    // Check if resource with that name exists.
    serviceDirectory *old_services = Datahandler::getServices();
    for( int i = 0; i < old_services->num_defined; i++ ){
        if( old_services->resourceName[i] == resource ) return -2;
    }
    
    // Create the app pool and ensure everything runs smoothly
    AppPool *pool = new AppPool();
    pool->setStatus( POOL::ACTIVE );
    
    // Initialise new app pools for services being deployed
    int n = pool->initializePool( config );
    if ( n ){
        pool->setStatus( POOL::DYING );
        FILE_LOG( logERROR ) 
            << "Unable to initialise appPool for configuration file at:"
            << nli() << "'" <<  config + "'.";
        delete pool;
        return n+10;
    }
    
    // Set the status correctly.
    if( POOL::parseAppStatus( status ) != POOL::ACTIVE ){
        pool->emptyPool();
        pool->setStatus( POOL::INACTIVE );
    }
    
    // Add Service to the master configuration file.
    Datahandler::addToConfig( resource, status, config );
    
    // Get service information and generate a new structure to replace it.
    serviceDirectory *new_services = new serviceDirectory( 
            old_services->root_directory,
            old_services->num_defined + 1
    );
            
    // Deep copy every service.    
    for (int i = 0; i < old_services->num_defined; i++)
    {
        // Deep copy variables.
        char *temp1 = new char[ old_services->resourceName[i].length() + 1];
        char *temp2 = new char[ old_services->configAddress[i].length() + 1];
        strcpy( temp1, old_services->resourceName[i].c_str() );
        strcpy( temp2, old_services->configAddress[i].c_str() );
        new_services->resourceName[i] = temp1;
        new_services->configAddress[i] = temp2;
        new_services->applicationPool[i] = old_services->applicationPool[i];
    }
    
    new_services->resourceName[old_services->num_defined] = resource;
    new_services->configAddress[old_services->num_defined] = config;
    new_services->applicationPool[old_services->num_defined] = pool;

    Datahandler::setServices( new_services );
    return 0;
}

int mServer::UPDATE(const std::string& target, const std::string& configAddress)
{
    serviceDirectory *services = Datahandler::getServices();
    for( int i = 0; i < services->num_defined; i++ )
    {
        if( target == services->resourceName[i] )
        {
            int c = services->applicationPool[i]->initializePool( configAddress );
            if( c )
            {
                DEACTIVATE( services->resourceName[i] );
                return c;
            }
            return 0;
        }
    }
    return -2;
}

int mServer::DELETE( const std::string& resource )
{
    serviceDirectory *services = Datahandler::getServices();
    
    for( int i = 0; i < services->num_defined; i++ ){
        if( services->resourceName[i] == resource ){ 
            
            DEACTIVATE( resource );
            services->applicationPool[i]->setStatus( POOL::DYING );
            
            // Delete the config file.
            if( !boost::filesystem::remove( services->configAddress[i] ) ) 
            { FILE_LOG( logWARNING ) << "Failed to delete: " << services->configAddress[i]; }
            
            // Delete the source files of the service.
            try {
                if( boost::filesystem::exists( services->applicationPool[i]->getWorkingDirectory() ) ) 
                    boost::filesystem::remove_all( services->applicationPool[i]->getWorkingDirectory() );
            } catch ( boost::filesystem::filesystem_error const & e ) {
                FILE_LOG( logERROR ) << "Machine Error on deleting: " << services->applicationPool[i]->getWorkingDirectory();
            }
            
            // Remove it from the master config.
            Datahandler::removeFromConfig( services->resourceName[i] );
            
            binItem *bag = new binItem( 
                services->applicationPool[i]->getWorkingDirectory(),
                services->resourceName[i],
                services->configAddress[i],
                services->applicationPool[i] );
                                        
            serviceDirectory *newSD = new serviceDirectory( services->root_directory, services->num_defined - 1);
             
            for( int j = 0, k = 0; j < services->num_defined-1; j++, k++ ){
                if( i == j ) k++;
                newSD->resourceName[j] = services->resourceName[k];
                newSD->configAddress[j] = services->configAddress[k];
                newSD->applicationPool[j] = services->applicationPool[k];
            }
            
            Datahandler::setServices( newSD );
            
            if(garbageCollector->first == NULL) garbageCollector->first = bag;
            else garbageCollector->last->next = bag; 
            garbageCollector->last = bag;
            return 0;
        }
    }
    return -1;
}

int mServer::flushServiceDirectory()
{
    serviceDirectory *services = Datahandler::getServices();
    
    for (int i=0; i < services->num_defined ; i++){
        
        if(services->applicationPool[i]->getStatus() == POOL::START){
            
            services->applicationPool[i]->setStatus( POOL::ACTIVE );
            
            //Initialise new app pools for services being deployed
            int n = services->applicationPool[i]->initializePool( services->configAddress[i] );
            if ( n ){
                services->applicationPool[i]->setStatus( POOL::INACTIVE );
                FILE_LOG( logERROR ) 
                    << "Unable to initialise appPool for configuration file at:"
                    << nli() << "'" <<  services->configAddress[i] + "'.";
                return -1;
            }
        }
        
        if( services->applicationPool[i]->getStatus() == POOL::STOP ){
            // Empty to pool to place it in a low resource intensive state.
            services->applicationPool[i]->emptyPool();
            services->applicationPool[i]->setStatus( POOL::INACTIVE );
        }      
    }
    return 0;  
}

void mServer::binMan( bin *gc, int *runToggle )   
{
    FILE_LOG( logINFO ) << "Bin man thread started.";
    // While program exists
    while( *runToggle ){
        
        // Check if there is anything in the bin.
        if( gc->first != NULL ){
            
            // Something in the bin, extract it and wait for 1 min.
            binItem *temp = gc->first;
            gc->first = gc->first->next;
            std::this_thread::sleep_for( std::chrono::seconds( 60 ) );
            
            // Delete objects.
            delete temp;
        } else {
            // Nothing to delete wait till the future.
            std::this_thread::sleep_for( std::chrono::seconds( 600 ) );
        }
    }
    
    FILE_LOG( logINFO ) << "Bin man shutting down, quickly finishing workload...";
    // Program is being shut down. While there are still things to delete.
    while( gc->first != NULL ){
        // Something in the bin, extract it.
        binItem *temp = gc->first;
        gc->first = gc->first->next;

        // Delete objects.
        delete temp;
    }
}