/* 
 * File:   httpResponse.cpp
 * Author: BACONL1
 * 
 * Created on 19 April 2016, 02:00
 */

#include "httpResponse.h"
//#include "httpMessage.h"




httpResponse::httpResponse(int socket, serverParameters* server ) 
: httpMessage( socket, server), HTTP_Status(0)
{
    header_dict = {
        {"Cache-Control ", &generalHeader.Cache_Control }
        , {"Connection ", &generalHeader.Connection }
        , {"Date ", &generalHeader.Date }
        , {"Pragma ", &generalHeader.Pragma }
        , {"Trailer ", &generalHeader.Trailer }
        , {"Transfer-Encoding ", &generalHeader.Transfer_Encoding }
        , {"Upgrade ", &generalHeader.Upgrade }
        , {"Via ", &generalHeader.Via }
        , {"Warning ", &generalHeader.Warning }
        , {"Accept-Ranges ", &responseHeader.Accept_Ranges }
        , {"Age ", &responseHeader.Age }
        , {"ETag ", &responseHeader.ETag }
        , {"Location ", &responseHeader.Location }
        , {"Proxy-Authenticate ", &responseHeader.Proxy_Authenticate }
        , {"Retry-After ", &responseHeader.Retry_After }
        , {"Server ", &responseHeader.Server }
        , {"Vary ", &responseHeader.Vary }
        , {"WWW-Authenticate ", &responseHeader.WWW_Authenticate }
        , {"Allow ", &entityHeader.Allow }
        , {"Content-Encoding ", &entityHeader.Content_Encoding }
        , {"Content-Language ", &entityHeader.Content_Language }
        , {"Content-Length ", &entityHeader.Content_Length }
        , {"Content-Location ", &entityHeader.Content_Location }
        , {"Content-MD5 ", &entityHeader.Content_MD5 }
        , {"Content-Range ", &entityHeader.Content_Range }
        , {"Content-Type ", &entityHeader.Content_Type }
        , {"Expires ", &entityHeader.Expires }
        , {"Last-Modified ", &entityHeader.Last_Modified }
    };
    
    generalHeader.Connection = "close";
    
    return;
}

const std::string& httpResponse::str(){
    std::stringstream ss;
    ss << "HTTP/" << version 
            << " " << HTTP_Status
            << " " << status_code_lkp[HTTP_Status]
            << std::endl;
    ss << transcribeHeaders();
    ss << std::endl;
    ss << message_body;
    message = ss.str();
    return message;    
}
    
int httpResponse::writeToSocket(){
    str();
    writeSocket();
}