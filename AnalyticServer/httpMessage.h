/* 
 * File:   httpMessage.h
 * Author: BACONL1
 *
 * Created on 22 April 2016, 11:24
 */

#include <iostream>
#include <string>
#include <map>
#include <cstring>
#include <unistd.h>

#include "log1.h"
#include "HTTPStructures.h"
#include "DataStructures.h"

#ifndef HTTPMESSAGE_H
#define	HTTPMESSAGE_H

class httpMessage {
    /*
     *This class represents a generic HTTP message (i.e request or response)
     * and contains generic methods and properties which are common to both
     * request and response messages.
     *This class serves as an abstract base to httpRequest and httpResponse
     * objects and is not intended to be initialised directly.
     * 
     *The structure of this class is based on the HTTP/1.1 specification as
     * detailed in RFC2616, available at:
     *          https://tools.ietf.org/html/rfc2616
    */
    

public:    
    
    httpMessage( int, serverParameters* );
    
    httpMessage& operator << (const std::string& str);
    HTTP::Status status();    //Getter function for current status
    
    bool checkHTTPCode( int );
    
    generalHeader_t generalHeader;
    entityHeader_t entityHeader;
    std::string message, message_body;  //strings holding the full message and message body

protected: 
    int sockfd; //file descriptor for input/output socket.
    int buffer_size;  //size of the socket input buffer (bytes)
    size_t charsRead;  //number of characters parsed
    HTTP::Status int_status; //current internal status of the object;

    std::string version = "1.1";
    const std::string delimiter = "\r\n";    //CRLF (see RFC 2616)
    
    int readSocket();   //Read from the input socket (buffer_size bytes) into the buffer
    int writeSocket();  //write the message to the output socket
    
    std::string transcribeHeaders();
    
    int parseHeader(const std::string& str);
    
    std::map<int, std::string> status_code_lkp = {
        {0, "Not Set"}
        , {100, "Continue"}
        , {101, "Switching Protocols"}
        , {102, "Processing"}
        , {200, "OK"}
        , {201, "Created"}
        , {202, "Accepted"}
        , {203, "Non-Authoritative Information"}
        , {204, "No Content"}
        , {205, "Reset Content"}
        , {206, "Partial Content"}
        , {207, "Multi-Status"}
        , {208, "Already Reported"}
        , {226, "IM Used"}
        , {300, "Multiple Choices"}
        , {301, "Moved Permanently"}
        , {302, "Found"}
        , {303, "See Other"}
        , {304, "Not Modified"}
        , {305, "Use Proxy"}
        , {306, "(Unused)"}
        , {307, "Temporary Redirect"}
        , {308, "Permanent Redirect"}
        , {400, "Bad Request"}
        , {401, "Unauthorized"}
        , {402, "Payment Required"}
        , {403, "Forbidden"}
        , {404, "Not Found"}
        , {405, "Method Not Allowed"}
        , {406, "Not Acceptable"}
        , {407, "Proxy Authentication Required"}
        , {408, "Request Timeout"}
        , {409, "Conflict"}
        , {410, "Gone"}
        , {411, "Length Required"}
        , {412, "Precondition Failed"}
        , {413, "Payload Too Large"}
        , {414, "URI Too Long"}
        , {415, "Unsupported Media Type"}
        , {416, "Range Not Satisfiable"}
        , {417, "Expectation Failed"}
        , {421, "Misdirected Request"}
        , {422, "Unprocessable Entity"}
        , {423, "Locked"}
        , {424, "Failed Dependency"}
        , {425, "Unassigned"}
        , {426, "Upgrade Required"}
        , {427, "Unassigned"}
        , {428, "Precondition Required"}
        , {429, "Too Many Requests"}
        , {430, "Unassigned"}
        , {431, "Request Header Fields Too Large"}
        , {451, "Unavailable For Legal Reasons"}
        , {500, "Internal Server Error"}
        , {501, "Not Implemented"}
        , {502, "Bad Gateway"}
        , {503, "Service Unavailable"}
        , {504, "Gateway Timeout"}
        , {505, "HTTP Version Not Supported"}
        , {506, "Variant Also Negotiates"}
        , {507, "Insufficient Storage"}
        , {508, "Loop Detected"}
        , {510, "Not Extended"}
        , {511, "Network Authentication Required"}
    };
    
    std::map<std::string,std::string*> header_dict;
};

#endif	/* HTTPMESSAGE_H */

