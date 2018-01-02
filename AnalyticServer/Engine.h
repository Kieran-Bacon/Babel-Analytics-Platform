#ifndef ENGINE_H
#define ENGINE_H

#include "log1.h"
#include "stdlib.h"
#include <algorithm>
#include <regex>

#include "EngineStructures.h"

/**
 * Handles the operation of a particular programs execution. Language 
 * independent blueprint establishing a general interface for child engines.
 */
class Engine {
public:
    
    /**
     * Initialise the parameters of the engine, and begin pre-processing if 
     * applicable.
     * @param wd - Working directory of the engines source code.
     * @param script - Name of the script holding the main function.
     * @return http status - Success if 200. 
     *                       Fatal server error if negative value.
     *                       Script error if positive non 200 value.
     */
    virtual int initialise( const std::string& wd, const std::string& script ){};
    
    /**
     * Run the engine on the payload received.
     * @param content_type - The format the payload is written in.
     * @param payload - An unprocessed string, body of http message received.
     * @return output - A string value of the output of the program.
     */
    virtual std::string execute( const std::string& content_type,
                                 const std::string& payload ){};
    
    /**
     * Return the engine to a runnable state if possible.
     * @return indicator - bool determining if the engine is suitable to be used again.
     */
    virtual int reset(){};
    
    /**
     * Modifies the input string to ensure no malicious action or accident
     * failure can as a result of the string.
     * @param str - Input string to ensured.
     * @return Output - escaped string.
     */
    static std::string toEscapedString( const std::string& str );
    
    /**
     * Construct a generic input structure for the engines use. Validates input. 
     * @param content_type - The format of the payload being passed.
     * @param payload - An unprocessed string containing variable(s).
     * @return input structure - A structure containing all relative information
     * about the payload. 
     */
    static input* parsePayload( const std::string& content_type, const std::string& payload );
    
    /**
     * Determines what Regex is necessary for the type being evaluated.
     * @param type - string representing a data structure.
     * @return regex - Regex object that matches on type.
     */
    static std::regex typeRegex( const std::string& type );

    ENGINE::Status status; /* The current state of the Engine */
    int http_code; /* HTTP code indicating validity of output */
};

#endif /* ENGINE_H */

