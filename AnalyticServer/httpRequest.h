#pragma once

//#include <iostream>
#include <sstream>
#include <cstring>
#include <unistd.h>

//#include <string>
//#include <map>

#include "log1.h"
#include "httpMessage.h"


#ifndef HTTPREQUEST_H
#define	HTTPREQUEST_H


class httpRequest: public httpMessage
{
    /*
     *This class represents a HTTP request received via a linux socket.
     *The constructor takes the file descriptor for the incoming port and reads
     *the incoming bytestream, parsing the message according to the HTTP/1.1 
     *specification as detailed in RFC2616, available at:
     *          https://tools.ietf.org/html/rfc2616
     *This class handles communication with the client as far as is required in
     *order for the full request packet to be received i.e. in the case of 
     *receiving an Expect: 100 Continue header.
     */
    
    public:
	httpRequest( int, serverParameters* );
        int readFromSocket();
        std::string stringifyMethod();
        

        requestHeader_t requestHeader;
        std::string resource, version;   //the resource uri as requested
        HTTP::Method method;

    private:
        int parseMessageHeader();   //Parse HTTP header from input buffer
	int parseMessageBody();     //Parse HTTP body from input buffer
        void parseMethod(const std::string & method_string);    //read HTTP method to enumerated type
};

#endif	/* HTTPREQUEST_H */
