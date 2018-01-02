#include "aServer.h"

void aServer::start()
{
    listen( socket_FD, server_param->queueSize );
    
    FILE_LOG( logINFO ) 
        << "Started Analytics Server - Port: " << server_param->portNum;
    
    *logToggle = *logToggle + 10;
    
    while( *runToggle ){
        // Wait for request, accept on new socket.
        int newSocket_FD = accept(socket_FD, 
                (sockaddr *) &client_address, (socklen_t *) &client_length);
        if (newSocket_FD < 0) {
            FILE_LOG(logERROR) 
                <<"Error on accept connection: "
                << strerror(errno) << ".";
        }
        
        if( !*runToggle ) break;
        
        // Start thread to process the connection in the new socket.
        processConnection( newSocket_FD );
        //std::thread (&aServer::processConnection, this, sockFd).detach();
    }
    FILE_LOG( logINFO ) << "Closing Analytics Server...";
    close( socket_FD );
    FILE_LOG( logINFO ) << "Analytics Server shutdown.";
}



void aServer::processConnection(int socket)
{
    // Start thread timer.
    auto startTime = std::chrono::high_resolution_clock::now();
    
    // Create HTTP request and response objects.
    httpRequest http_reqt( socket, Datahandler::getAnalytics() );
    httpResponse http_resp( socket, Datahandler::getAnalytics() );
    
    int n = http_reqt.readFromSocket();
    if( n == -1)
    {
        // For Post method, content length corrupted or non existent.
        http_resp.HTTP_Status = 400;
        http_resp << "Malformed request - content length error.";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING ) 
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
            << "Received message timed out before parsing completed.";
        return;
    }
    else if( n == -3 )
    {
        // Error during reading, respond and return.
        http_resp.HTTP_Status = 400;
        http_resp << "Error reading HTTP request";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING ) << "Analytics Error reading message from socket."; 
        return;
    }
    
    // Collect service information.
    int sid;
    serviceDirectory *services = Datahandler::getServices();
    if( (http_reqt.method == HTTP::GET || http_reqt.method == HTTP::POST) 
        && services->num_defined == 0 )
    {
        http_resp.HTTP_Status = 204;
        http_resp << "Unfortunately we are currently hosting no services.";
        http_resp.writeToSocket();
        close(socket);
        FILE_LOG( logWARNING ) << "Receiving requests when not hosting services.";
        return;
    } else if(http_reqt.method == HTTP::GET || http_reqt.method == HTTP::POST){
        // Find the index of the resource.
        for(sid = 0; sid < services->num_defined; sid++)
        {
            if(http_reqt.resource == services->resourceName[sid]){
                // Service found.
                break;
            }

            //Resource has not been matched
            if( sid == services->num_defined - 1){
                // Service not found.
                http_resp.HTTP_Status = 404; 
                http_resp.writeToSocket();
                close(socket);

                FILE_LOG(logWARNING) 
                    << "HTTP status 404 sent in response to request for resource at: '"
                    << http_reqt.resource << "'.";

                return;
            }

        }
    }
    
    Engine *eng = NULL;
    
    switch (http_reqt.method)
    {
        case HTTP::GET:
            
            http_resp.HTTP_Status = services->applicationPool[sid]->GET_status();
            
            if ( services->applicationPool[sid]->GET_status() == 200 ){
                http_resp << services->applicationPool[sid]->GET_HTML();
            } else {
                http_resp.responseHeader.Location 
                    = services->applicationPool[sid]->GET_HTML();
            }
            break;

        case HTTP::POST:
            // Collect engine from the service's application pool.
            eng = services->applicationPool[sid]->getApp();
            
            // No engine returned.
            if( eng == NULL ){
                http_resp.HTTP_Status = 404;
                http_resp << "Service is deactivated.";
                break;
            }
            
            // Run engines main function with the message payload.
            http_resp << eng->execute( http_reqt.entityHeader.Content_Type, 
                                       http_reqt.message_body);
            
            // Check operation of the engine was successful.
            switch (eng->status){
                case ENGINE::OK:
                    http_resp.HTTP_Status = 200;
                    break;
                case ENGINE::SESSION_ERROR:
                case ENGINE::CONNECTION_ERROR:
                    http_resp.HTTP_Status = 500;
                    break;               
                case ENGINE::EXECUTE_ERROR:
                    if( http_reqt.checkHTTPCode( eng->http_code ) ){
                        http_resp.HTTP_Status = eng->http_code;
                    } else 
                    { 
                        http_resp.HTTP_Status = 500;
                        FILE_LOG( logERROR ) 
                            << http_reqt.resource 
                            << " incorrectly used program_status variable "
                            << "during execution.";
                    }
                    break;
                default:
                    http_resp.HTTP_Status = 500;
                    break;
            }
            break;
        case HTTP::TRACE:
            http_resp << http_reqt.message;
            http_resp.HTTP_Status = 200;
            break;
            
        case HTTP::OPTIONS:
            http_resp.HTTP_Status = 200;
            http_resp << "Get Methods:\n"
                      << "\t /[resource] - Get the HTML representation for the service.\n"
                      << "Post Methods:\n"
                      << "\t /[resource] - Post inputs to service for computation.";
            break;
        default:
            http_resp.HTTP_Status = 405;    //HTTP "Method Not Allowed"
            break;
    }
    
    // Respond to message and close connection.
    http_resp.writeToSocket();
    close(socket);
    
    std::chrono::duration<double, std::milli> timer
        = std::chrono::high_resolution_clock::now() - startTime;
    std::string reason;
    if( http_resp.HTTP_Status != 200 ) reason = http_resp.message_body;
    
    if( http_reqt.method == HTTP::POST ){
        FILE_LOG( Analytics ) 
            << http_reqt.resource << " " 
            << timer.count()/1000 << " "
            << "0" << " "
            << http_resp.HTTP_Status << " "
            << reason;
    } else {
        FILE_LOG( logINFO ) 
            << HTTP::stringify( http_reqt.method ) << " "
            << http_reqt.resource << " "
            << http_resp.HTTP_Status << " "
            << reason;
    }
    
    // Return engine to it's respective application pool for evaluation.
    if( eng )
    {
        int s = services->applicationPool[sid]->appendNewApp( eng );
        if( s ){ 
            FILE_LOG( logWARNING ) 
                << "Unable to append engine to application pool for "
                << "resource at: '" << http_reqt.resource << "'.";
        }
    }
}