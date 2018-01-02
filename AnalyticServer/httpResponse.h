/* 
 * File:   httpResponse.h
 * Author: BACONL1
 *
 * Created on 19 April 2016, 02:00
 */

#include <string>
#include <sstream>
#include <map>

#include "httpMessage.h"


#ifndef HTTPRESPONSE_H
#define	HTTPRESPONSE_H

class httpResponse: public httpMessage {
public:
    httpResponse( int, serverParameters* );
    int writeToSocket();    
    const std::string& str();

    responseHeader_t responseHeader;
    int HTTP_Status;     //HTTP Status-code
};

#endif	/* HTTPRESPONSE_H */

