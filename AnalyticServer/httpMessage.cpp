#include "httpMessage.h"

httpMessage::httpMessage(int socket, serverParameters *server ){
    charsRead = 0;
    sockfd = socket;
    buffer_size = server->bufferSize;
}

httpMessage& httpMessage::operator << (const std::string& str){
    message_body.append(str);   
    entityHeader.Content_Length = std::to_string(message_body.length());
    return *this;
}

HTTP::Status httpMessage::status(){
    return int_status;
}


int httpMessage::readSocket()
{
    // Define a input buffer and pre-set its contents.
    char buffer[buffer_size];
    bzero(buffer, buffer_size);
    
    // Read from the socket a buffer sized amount, into the buffer.
    int n = read(sockfd, buffer, buffer_size - 1);
    if (n < 0) {
        FILE_LOG(logERROR) 
            << "Error on socket read: " << nli() << strerror(errno);
        int_status = HTTP::SOCKET_ERR;
    }
    
    // Concatenate previously read buffers together.
    message.append(buffer);
}


int httpMessage::writeSocket()
{
    int n;
    n = write(sockfd, message.c_str(), message.length());	//write data to socket
    if (n < 0) {
        FILE_LOG(logERROR) 
            << "Error on socket write: " << nli() << strerror(errno);
        int_status = HTTP::SOCKET_ERR;
    }
}



std::string httpMessage::transcribeHeaders(){

    std::stringstream header_lines;
    
    for(auto &ent : header_dict) //iterate through each element in the header fields map
    {
        if (!(*ent.second).empty()) //check if header value non-empty
        {
            header_lines << ent.first << ": " << (*ent.second) << std::endl;
        }
    }

    return header_lines.str();
}

/* Parse message header attributes.
 * parm@ str - Substring of message's header, containing a key value pair joined 
 *             by ': '.  
 */
int httpMessage::parseHeader(const std::string& str){
    
    /* str is split into key value pair using the ':' char as a delimiter. */
    std::stringstream ss(str);
    std::string key, val;
    std::getline(ss, key, ':');
    std::getline(ss, val);

    /* Header_dict's keys are currently set within the httpRequest 
     * constructor.
     * Find if they key is present and assign it's value.
     */    
    if (header_dict.find(key) != header_dict.end()){
        // Remove white space before and after the key.
        size_t i = val.find_first_not_of( ' ' );
        if( i == std::string::npos ) *(header_dict[key]) = "";
        *(header_dict[key]) = val.substr(i, val.find_last_not_of( ' ' )-i+1);
        
        
    } else {
        FILE_LOG(logDEBUG3) << "Unrecognised header field detected: " << key;
        return -1;
    }
    
    return 0;
}

bool httpMessage::checkHTTPCode(int code ){
    std::map<int, std::string>::iterator it = status_code_lkp.find( code );
    if( it != status_code_lkp.end() )
    { 
        //Code found
        return true;
    }
    else
    {
        //code not found
        return false;
    }
}