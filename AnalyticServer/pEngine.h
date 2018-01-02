#ifndef PENGINE_H
#define PENGINE_H

#include <string>
#include <cstring>
#include <iostream>
#include <thread>

#include "Engine.h"
#include "pythonStructures.h"
#include "/usr/include/python2.7/Python.h"

/**
 * Handles operations of programs written in the programming language Python.
 */
class pEngine : public Engine
{
public:
    
    /**
     * Sets default values for the engine.
     */
    pEngine();
    
    /**
     * Deletes the stored parameters of the engine.
     */
    ~pEngine();
    
    /** @OVERRIDDEN
     * Initialises the engine by starting a thread to house a python 
     * interpreter.
     * @param wd - Working Directory of the programs source files.
     * @param script - The name of the script that houses the main function.
     * @return status - Indicates if the process was successful.
     */
    int initialise( const std::string& wd, const std::string& script );
    
    /** @OVERRIDDEN
     * Parses the input values via parent class and communicates the with thread
     * through shared parameters structure to begin start computation. 
     * @param content_type - Format of payload, used in parse.
     * @param payload - Unprocessed string to be sent to python interpreter.
     * @return output - The value produced by the python thread.
     */
    std::string execute( const std::string& content_type,
                         const std::string& payload );
    
    /** @OVERIDDEN
     * Resets the engine by starting a new thread as thread.
     * @return status - Indicates if reset was successfull.
     */
    int reset();
    
    /**
     * Operates the Python interpreter through the c api. Loads program and runs
     * pre-processing before waiting for input to compute.
     * @param params - shared information point holding pointers to engine
     * specific information. 
     */
    static void runEngine( interface* params );
    
    interface *parameters; /* Pointer to structure shared between engine and 
                            * python thread. */
    
private:
    
    /**
     * Converts a filename/filepath to a valid python import string. Assumes the
     * filename is valid address as Python interpreter check anyways.
     * @param filename - valid filepath or name to main script location.
     * @return pythonString - valid import string. 
     */
    std::string pyImportString( const std::string& filename );
    
};

#endif /* PENGINE_H */

