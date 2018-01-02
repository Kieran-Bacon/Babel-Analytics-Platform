#include "httpRequest.h"


#include <sstream>



httpRequest::httpRequest( int socket, serverParameters* server):
             httpMessage( socket, server){
    
    //initialise the header map for this class
    header_dict = {
            {"Cache-Control", &generalHeader.Cache_Control}
            , {"Connection", &generalHeader.Connection}
            , {"Date", &generalHeader.Date}
            , {"Pragma", &generalHeader.Pragma}
            , {"Trailer", &generalHeader.Trailer}
            , {"Transfer-Encoding", &generalHeader.Transfer_Encoding}
            , {"Upgrade", &generalHeader.Upgrade}
            , {"Via", &generalHeader.Via}
            , {"Warning", &generalHeader.Warning}
            , {"Accept", &requestHeader.Accept}
            , {"Accept-Charset", &requestHeader.Accept_Charset}
            , {"Accept-Encoding", &requestHeader.Accept_Encoding}
            , {"Accept-Language", &requestHeader.Accept_Language}
            , {"Authorization", &requestHeader.Authorization}
            , {"Expect", &requestHeader.Expect}
            , {"From", &requestHeader.From}
            , {"Host", &requestHeader.Host}
            , {"If-Match", &requestHeader.If_Match}
            , {"If-Modified-Since", &requestHeader.If_Modified_Since}
            , {"If-None-Match", &requestHeader.If_None_Match}
            , {"If-Range", &requestHeader.If_Range}
            , {"If-Unmodified-Since", &requestHeader.If_Unmodified_Since}
            , {"Max-Forwards", &requestHeader.Max_Forwards}
            , {"Proxy-Authorization", &requestHeader.Proxy_Authorization}
            , {"Range", &requestHeader.Range}
            , {"Referer", &requestHeader.Referer}
            , {"TE", &requestHeader.TE}
            , {"User-Agent", &requestHeader.User_Agent}
            , {"Allow", &entityHeader.Allow}
            , {"Content-Encoding", &entityHeader.Content_Encoding}
            , {"Content-Language", &entityHeader.Content_Language}
            , {"Content-Length", &entityHeader.Content_Length}
            , {"Content-Location", &entityHeader.Content_Location}
            , {"Content-MD5", &entityHeader.Content_MD5}
            , {"Content-Range", &entityHeader.Content_Range}
            , {"Content-Type", &entityHeader.Content_Type}
            , {"Postman-Token", &entityHeader.Postman_Token}
            , {"Expires", &entityHeader.Expires}
            , {"Last-Modified", &entityHeader.Last_Modified}
            , {"Username", &requestHeader.Username }
            , {"Access-Token", &requestHeader.Access_Token }
        };
    
    int_status = HTTP::READ_HEADER;
}

std::string httpRequest::stringifyMethod(){
    if( method == HTTP::OPTIONS )       return "OPTIONS";
    else if ( method == HTTP::GET )     return "GET";
    else if ( method == HTTP::HEAD )    return "HEAD";
    else if ( method == HTTP::POST )    return "POST";
    else if ( method == HTTP::PUT )     return "PUT";
    else if ( method == HTTP::DELETE )  return "DELETE";
    else if ( method == HTTP::TRACE )   return "TRACE";
    else if ( method == HTTP::CONNECT ) return "CONNECT";
    else                                return "ERROR";
}

int httpRequest::readFromSocket()
{
    // Begin time recording to exit in event of timeout.
    auto startTime = std::chrono::system_clock::now();
    std::chrono::duration<double> timer;
    
    do {
        // Read in from the socket a set amount of the message.
        readSocket();
        // Parse the message header from the buffer to determine if all is read.
        parseMessageHeader();
        // Adjust time record as to allow for timeouts.
        timer = std::chrono::system_clock::now() - startTime;
    } while ( int_status == HTTP::READ_HEADER && timer.count() < 10 && resource != "" );
    
    // Check if error occurred, report cause.
    if( resource == "" ) return -3;
    else if( int_status == HTTP::READ_HEADER ) return -2;

    if (requestHeader.Expect == "100 Continue") {       //Check whether the client is using "Expect: 100 Continue" method
        FILE_LOG(logDEBUG3) 
            << "Received 'Expect: 100 Continue' header. Sending 100-continue "
            << "confirmation.";

        write(sockfd, "HTTP/1.1 100 Continue", 21);   //Confirm transmission of message body
     }
     
    // Extract the message body if the content length is set.
    if( entityHeader.Content_Length.length()!=0 ){
        
        // Ensure the content length is not malformed.
        std::string length = entityHeader.Content_Length;
        if( !(!length.empty() && 
            std::find_if( length.begin(), length.end(), 
            [](char c) { return !std::isdigit( c ); }) == length.end()) )    
        {
            FILE_LOG(logDEBUG3) 
                << "Error parsing HTTP request. Could not determine HTTP body" 
                << "length from message headers. HTTP request content length: " 
                << entityHeader.Content_Length;  
            int_status = HTTP::READ_ERR;
            return -1;
        }
        
        // Reset time counter ( Message bodies should be longer )
        startTime = std::chrono::system_clock::now();
        parseMessageBody();
        
        while ( int_status == HTTP::READ_BODY && timer.count() < 60 ) {
            // Read from the socket any new characters into the message buffer.
            readSocket();
            // Parse the remaining characters in the message buffer.
            parseMessageBody();
            // Adjust time counter.
            timer = std::chrono::system_clock::now() - startTime;
        }
        if( int_status == HTTP::READ_BODY ) return -2;
            
    } else if ( method == HTTP::POST ) {
        int_status = HTTP::READ_ERR;
        FILE_LOG( logDEBUG3 ) << "Message did not have a content length.";
        return -1;
    } else {
        int_status = HTTP::COMPLETE;
    }

    if (int_status == HTTP::COMPLETE){
        FILE_LOG( logDEBUG3 ) << "HTTP request parsed successfully.";
        return 0;
    } else {
        FILE_LOG( logDEBUG3 ) << "HTTP request has failed to be parsed.";
        int_status = HTTP::READ_ERR;
        return -3;
    }
}

int httpRequest::parseMessageHeader() 
{
    /* Substring of Request message to hold individual lines of information */
    std::string token;
    /* Concatenation of all Token information for logger purposes. */
    std::string attributes = ""; //Concatenation of all token information.

    size_t pos = 0;
    
    /* While we are have not reached the end of the header: 
     * -Check Request status
     * -Check delimiter is not present in the remaining message.
     */
    while ((int_status == HTTP::READ_HEADER) &
    ((pos = message.substr(charsRead).find(delimiter)) != std::string::npos)) {

        /* Capture a string from last read position to the next delimiter. */
        token = message.substr(charsRead, pos);
        attributes = attributes + nli() + token;
        
        std::stringstream sl(token);
        
        if( resource == "" ) {
            /* First line of request */
            std::string mtd;
            std::getline(sl, mtd, ' ');
            std::getline(sl, resource, ' ');
            std::getline(sl, version, ' ');
            parseMethod(mtd);
        } else if( token.length() > 0 ){
            /* Attributes of request following the declaration */
            parseHeader(token);
        } else {
            /* Empty line in-countered (i.e CRLF) */
            int_status = HTTP::READ_BODY;
        }
            
        charsRead += pos + delimiter.length();
    }
    
    FILE_LOG(logDEBUG4) << "Message Headers: " << attributes;
     
    return (0);
}



int httpRequest::parseMessageBody() 
{
    std::string str = message.substr(charsRead);
    
    if (str.length() == std::stoi(entityHeader.Content_Length))
    {
        message_body = str;
        int_status = HTTP::COMPLETE;
    } else if(str.length() > std::stoi(entityHeader.Content_Length))
    {
        FILE_LOG(logDEBUG3) << "Error reading HTTP message body.";
        int_status = HTTP::READ_ERR;
    }

    return (0);
}

/* This is a helper function for converting method strings to elements of
 * the 'methodEnum' enumerated type.
 */
void httpRequest::parseMethod(const std::string & method_string)
{
    if (method_string == "OPTIONS")      method = HTTP::OPTIONS;
    else if (method_string == "GET")     method = HTTP::GET;
    else if (method_string == "HEAD")    method = HTTP::HEAD;
    else if (method_string == "POST")    method = HTTP::POST;
    else if (method_string == "PUT")     method = HTTP::PUT;
    else if (method_string == "DELETE")  method = HTTP::DELETE;
    else if (method_string == "TRACE")   method = HTTP::TRACE;
    else if (method_string == "CONNECT") method = HTTP::CONNECT;
    else {
        FILE_LOG(logERROR)<<"Error reading HTTP request: Method not recognised";
        int_status = HTTP::READ_ERR;
    }
}