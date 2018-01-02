#include "Server.h" 

int Server::initialiseSocket( serverParameters *serverInformation )
{
    // Assign Server information
    server_param = serverInformation;
    
    bzero((char *) &server_address, sizeof(server_address));
    client_length = sizeof( client_address );

    server_address.sin_family = AF_INET;
    // htons() converts a port number in host byte order to network byte order.
    server_address.sin_port = htons( serverInformation->portNum );
    //IP address of host. INADDR_ANY.
    server_address.sin_addr.s_addr = INADDR_ANY; 	
    
    // Create a socket connect on parameters specified.
    socket_FD = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_FD < 0) {
        FILE_LOG(logERROR)<< "Error opening socket: " << strerror(errno) << ".";
        return -1;
    }
    
    // Bind thread to socket.
    if ( bind(socket_FD, 
             (sockaddr *) &server_address, sizeof(server_address)) > 0 ){
        FILE_LOG(logERROR) 
            << "Error on binding to socket: " << strerror(errno) << ".";
        return -2;
    }
    
    return socket_FD;
}