#include "Engine.h"

std::string Engine::toEscapedString(const std::string& str)
{
    std::string out_str;
    std::stringstream out_stream(str);
    
    // Loop through characters and ensure characters safe.
    out_stream << "\"";
    for (const char& c:str){
        switch (c)
        {
            case '\"':
                out_stream << "\\\"";
                break;
            case '\n':
                out_stream << "\\n";
                break;
            case '\t':
                out_stream << "\\t";
                break;
            case '\r':
                out_stream << "\\r";
                break;
            case '\\':
                out_stream << "\\\\";
                break;
            default:
                out_stream << c;
        }       
    }
    out_stream << "\"";
    
    getline(out_stream,out_str,'\0');
    return out_str;   
}

input* Engine::parsePayload(const std::string& content_type,
                            const std::string& payload)
{
    // Create input structure to return.
    input *newInput = new input;
    
    if( content_type == "application/x-www-form-urlencoded" )
    {
        // Determine the number of variables in the payload
        size_t num_variables = std::count( payload.begin(),payload.end(),'&')+1;
        size_t checker = std::count( payload.begin(), payload.end(), '=' );
        
        // Ensure the data is in the correct form.
        if( num_variables != checker )
        {
            newInput->length = -1;
            newInput->type = new std::string( "Message" );
            newInput->variables = new std::string( payload );
            return newInput;
        }
        
        // Construct the variables the input will contain pointers too.
        newInput->length = num_variables;
        newInput->type = new std::string[ num_variables ];
        newInput->variables = new std::string[ num_variables ];
        
        int count = 0;
        std::string i, t, v;
        size_t ts, vs;
        i = payload;
        
        // While there is a type value pair.
        while( (ts = i.find('=')) != std::string::npos )
        {
            // Extract the type and shorten the payload string.
            t = i.substr( 0, ts );
            i = i.substr( ts+1 );
            
            // If there is a another type-variable after this variable
            if( (vs = i.find('&')) != std::string::npos )
            {
                // Extract the variable and shorten the payload string.
                v = i.substr(0, vs);
                i = i.substr( vs + 1 );
            } else {
                // Set the payload string as variable as only variable is left.
                v = i;
            }
            
            // Check if type and variable match correctly.
            if( t == "string" 
            || (std::regex_match( v, typeRegex( t ) ) 
            && !std::regex_match( "ERROR", typeRegex( t ) ) ) ){
                // Add the type and variable into the input structure.
                newInput->type[count] = t;
                newInput->variables[count]  = v;
                count++;  
            } 
            else 
            {
                // Delete structure and report error, stop computation.
                delete newInput;
                FILE_LOG( logDEBUG4 ) 
                    << "Variable error: type - " << t << " value - " << v;
                
                input *error = new input;
                error->type = new std::string( t );
                error->variables = new std::string( v );
                error->length = -1;
                return error;
            }    
        }
        return newInput;
    }
    else
    {
        // Either expected to simply send the entire payload or un-handled 
        // content type.
        newInput->length = 1;
        newInput->type = new std::string[1];
        newInput->type[0] = "string";
        newInput->variables = new std::string[1];
        newInput->variables[0] = payload;
        return newInput;
    }
}

std::regex Engine::typeRegex( const std::string& type) 
{
    if ( type == "int" || type == "long" )   return std::regex("^[-+]?[0-9]*$");
    else if (type == "float" )
        return std::regex("^[-+]?[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?$");
    else                                     return std::regex( "^ERROR$" );
}