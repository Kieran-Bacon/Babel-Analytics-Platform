#include "rEngine.h"

rEngine::rEngine()
:rc(new Rconnection())
{
    //Establish connection to R session
    int i = rc->connect();
    if (i) {
        FILE_LOG( logDEBUG2 ) << "R connection response code: " << i;
        status = ENGINE::CONNECTION_ERROR;
    }
    status = ENGINE::OK;
}

rEngine::~rEngine()
{
    delete rc;   
}

int rEngine::initialise(const std::string& wd, const std::string& script)
{
    // Construct the set working directory string.
    std::string setWd = "setwd(" + toEscapedString( wd ) + ")";
    std::string source = "source(" + toEscapedString( script ) + ")";
    
    // Run set wd command
    runCommand( setWd );
    if( http_code != 200 ){
        FILE_LOG( logDEBUG4 ) << "Failed to set working directory";
        status = ENGINE::SESSION_ERROR;
        return -1;
    }
    
    // Source the file
    std::string resp = runCommand( source );
    if( http_code != 200 ){
        FILE_LOG( logDEBUG4 ) 
            << "Failed to source file with reason:" << nli()
            << resp;
        status = ENGINE::SESSION_ERROR;
        return -2;
    }
    
    // Setup function
    std::string check = runCommand( "paste0( exists( 'setup' ) )" );
    if( http_code == 200 && check == "TRUE" ){
        // Execute the set up function
        runCommand( "setup()" );
        if( http_code != 200 ){
            FILE_LOG( logDEBUG4 ) << "Failed running setup function.";
            status = ENGINE::EXECUTE_ERROR;
            return -3;
        }
    }
    return 0;
}

std::string rEngine::execute(const std::string& content_type, const std::string& payload)
{
    // Split the input into its variables.
    input *inputs = parsePayload( content_type, payload );
    
    // Construct the main function command.
    std::string command = "main(";
    for( int i = 0; i < inputs->length; i++ ){
        command = command + inputs->variables[i];
        if( i != inputs->length -1) command = command + ",";
    }
    command = command + ")";
    
    // Run the command and return the response.
    std::string resp = runCommand( command );
    if( http_code != 200 ) status = ENGINE::EXECUTE_ERROR;
    return resp;
}

int rEngine::reset()
{
    // No reset needed.
    return 0;
}

std::string rEngine::runCommand( const std::string& cmd)
{
    std::stringstream rCommand;
    rCommand << "program_status = 200" << "\n"
             << "tryCatch( paste0(" << cmd << "),error=function(e) {" << "\n"
             << "program_status <<- 400" << "\n"
             << "paste0(e)" << "\n"
             << "})";
    
    std::string sCommand = "paste0(program_status)";
    std::string out_str;
    
    Rstring *t = (Rstring*) rc->eval((rCommand.str()).c_str());
    Rstring *s = (Rstring*) rc->eval(sCommand.c_str());
    if (t && s) //command executed in R session
    {
        out_str = t->string();
        
        std::string status = s->string();
        if( !status.empty() && std::find_if( status.begin(), status.end(), 
            [](char c) { return !std::isdigit( c ); }) == status.end())
        {
            http_code = std::stoi(s->string());
        } else {
            status = ENGINE::EXECUTE_ERROR;
            http_code = 500;
            FILE_LOG( logDEBUG4 ) << "R returned non integer status value.";
        } 
    }
    else
    {
        status = ENGINE::EXECUTE_ERROR;
        http_code = 500;
        out_str = "No output was generated for given input.";
    }
    
    delete t; 
    delete s;

    return out_str;
}