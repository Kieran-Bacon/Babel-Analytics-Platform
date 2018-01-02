#include "pEngine.h"

pEngine::pEngine()
{
    status = ENGINE::OK;
    http_code = 200;
    parameters = new interface( &http_code );
}

pEngine::~pEngine(){
    // Thread is waiting for input.
    
    // Signal thread to continue
    input *close = new input;
    close->length = -1;
    parameters->payload = close; 
    
    {
        pthreadSwitch toggle;
        while( parameters->output == NULL 
            && *parameters->stage != 4 ){}
    }
    
    // Thread is closed. Delete shared structure.
    
    delete parameters;
}

int pEngine::initialise( const std::string& dir, const std::string& script )
{
    // Store service particular information.
    parameters->directory = dir;
    parameters->main = pyImportString( script );
    
    {
        pthreadSwitch toggle;
        // Allow Python threads to begin work and start threads.
        std::thread python( pEngine::runEngine, parameters );
        python.detach();
        
        // While thread is working towards a waiting state or error, poll.
        while( *parameters->stage != 2 && *parameters->stage != 4 ){}
    }
 
    // Return success or error code.
    if( http_code == 200  ) return 0;
    else if(http_code==-1)FILE_LOG(logDEBUG1)<<"Failed to load Python session.";
    else if(http_code==-2)FILE_LOG(logDEBUG1)<<"Failed to load program file.";
    else if(http_code==-3)
        FILE_LOG(logDEBUG1)<<"Program flagged error during setup.";
    else if(http_code==-4)
        FILE_LOG(logDEBUG1)<<"Main function has not been defined.";
    return http_code;
}

std::string pEngine::execute( const std::string& content_type, 
                              const std::string& payload )
{
    // Parse input check to see if valid.
    parameters->payload = parsePayload( content_type, payload );
    if( parameters->payload->length == -1)
    {
        status = ENGINE::EXECUTE_ERROR;
        http_code = 404;
        std::stringstream stream;
        stream << "Bad request data: input invalid\ntype: "
               << parameters->payload->type[0] << "\t value: " 
               << parameters->payload->variables[0];
        return stream.str();
    }
    
    {
        // Allow python threads to resume work.
        pthreadSwitch toggle;
        
        // While output is still to be created (or error), poll.
        while( parameters->output == NULL && *parameters->stage != 4 ){}
    }
    // Thread terminates.
    
    //Program flagged error.
    if( http_code != 200 ) status = ENGINE::EXECUTE_ERROR;
    if( http_code == -1 )
    {
        // if user incorrectly assigns non int value to program_status
        FILE_LOG( logERROR ) 
            << parameters->directory << parameters->main 
            << " Incorrectly used program_status during execution.";
        http_code = 200;
        return *parameters->output ;
    }
    else if( http_code == -5 )
    {
        // No return value from the main function.
        status = ENGINE::EXECUTE_ERROR;
        http_code=500;
        return "Service did not produce an output for that input.";
    }
    return *parameters->output;
}

int pEngine::reset()
{
    // Is the thread still in the waiting stage.
    bool runCheck = *parameters->stage == 2;
    
    // Reset values
    *parameters->stage = 1;
    *parameters->program_status = 0;
    
    // Garbage collect old parameters structures.
    input *GCOne = parameters->payload;
    std::string *GCTwo = parameters->output;
    parameters->payload = NULL;
    parameters->output = NULL;
    delete GCTwo;
    delete GCOne;
    
    if( runCheck ) return 0;
    else return initialise( parameters->directory, parameters->main );    
}

std::string pEngine::pyImportString( const std::string& filename){
    // Assuming valid path with program name correct.
    
    std::string str = filename;
    // Remove relative reference path starter.
    if( str[0] == '.' ) str = str.substr( 2 );
    
    // Replace folder delimiter with python delimiter.
    std::replace( str.begin(), str.end(), '\\', '.');
    
    // Remove the extension
    std::size_t index = str.find( '.' );
    if( index != std::string::npos ) return str.substr(0, index);
    return str;
}

void pEngine::runEngine( interface *params )
{
    // Begin Python thread and declare all variables.
    pthreadState state;
    PyObject *module, *program; //Module holders
    PyObject *setup, *main; //Function holders
    PyObject *empty, *input, *status, *value; //Variable holders
    empty = PyTuple_New(0);
    
    // Append the working directory to system path so that the script may be
    // imported.
    PyRun_SimpleString( "import sys" );
    std::string command = "sys.path.append( '" + params->directory + "')";
    PyRun_SimpleString( command.c_str() );
    
    // Create a main module to run script in check if successful.
    module = PyImport_AddModule("__main__");
    if( module != NULL ){
        
        // Import the main script and check if successful.
        program = PyImport_Import(PyString_FromString(params->main.c_str()));
        if( program != NULL )
        {
            // Assign a global variable within the module to indicate state and
            // give program ability to communicate information to the user.
            PyObject_SetAttrString( program, 
                                "program_status", PyInt_FromLong( (long) 200 ));
            
            // Check if setup function is defined and run if it does.
            setup = PyObject_GetAttrString( program, "setup" );
            if( setup && PyCallable_Check( setup )){
                value = PyObject_CallObject( setup, empty );
                
                //Check status to ensure no non syntax errors thrown by program.
                status = PyObject_GetAttrString( program, "program_status");
                *params->program_status = PyInt_AsLong( status );
                if( *params->program_status != 200 )
                {
                    // Error on set up, go to exit stage, release lock and exit.
                    state.releaseLock();
                    *params->program_status = -3;
                    *params->stage=4;
                    exit;
                }
            }
            
            // Check main function is defined and callable.
            main = PyObject_GetAttrString( program, "main" );
            if ( !main || !PyCallable_Check( main ) )
            {
                state.releaseLock();
                *params->program_status = -4;
                *params->stage = 4;
                exit;
            }
            
            // Exit setup section, move to wait stage and wait for input.
            state.releaseLock();
            *params->stage = 2;
            while( params->payload == NULL ){}
            state.gainLock();
            
            if( params != NULL && params->payload->length != -1)
            {
                // Move into stage three if input is valid.
                *params->stage = 3;
                
                // Create input argument tuple
                input = PyTuple_New( params->payload->length );
                for( int i = 0; i < params->payload->length; i++ ){

                    std::string type = params->payload->type[i];

                    if( type == "string" ){
                        PyTuple_SetItem( input, i, PyString_FromString( 
                                params->payload->variables[i].c_str() ));
                    }
                    else if ( type == "int" || type == "long" )
                    {
                        PyTuple_SetItem( input, i, PyInt_FromLong( 
                                std::stol(params->payload->variables[i]) ));
                    }
                    else if ( type == "float" )
                    {
                        PyTuple_SetItem( input, i, PyFloat_FromString( 
                                PyString_FromString(
                                params->payload->variables[i].c_str()),NULL));
                    }
                }

                // Run main function.
                value = PyObject_CallObject( main, input );
                if( value != NULL ){
                    // Ensure returned value is a string.
                    value = PyObject_Str( value );
                    // Construct the output of the program.
                    status = PyObject_GetAttrString( program, "program_status");
                    *params->program_status = PyInt_AsLong( status );
                    params->output = new std::string(PyString_AsString( value ));
                    *params->stage = 4;
                } else {
                    // Indicate no return value.
                    *params->program_status = -5;
                    *params->stage = 4;
                }
            }
            else
            {
                // Engine being deleted, move to exit stage.
                *params->stage = 4;
            }
        }
        else 
        {
            // Error on file load.
            *params->program_status = -2;
            *params->stage = 4;
        }
    } 
    else
    {
        // Error on opening python main module.
        *params->program_status = -1;
        *params->stage = 4;
    } 
}