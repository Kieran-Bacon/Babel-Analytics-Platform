/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/* 
 * File:   pythonStructures.h
 * Author: bammins
 *
 * Created on 05 April 2017, 16:41
 */

#ifndef PYTHONSTRUCTURES_H
#define PYTHONSTRUCTURES_H

#include "/usr/include/python2.7/Python.h"

/**
 * Structure used to define and destroy the python c API. 
 */
struct pythonInitialise
{
    pythonInitialise(){ Py_InitializeEx(1); PyEval_InitThreads(); }
    ~pythonInitialise(){ Py_Finalize(); }
};

/**
 * Structure used to define and hold python thread state to allow for multiple
 * instances of the interpreter.
 */
struct pthreadState
{
    pthreadState()      { _state = PyGILState_Ensure(); }
    void gainLock()     { _state = PyGILState_Ensure(); }
    void releaseLock()  { PyGILState_Release( _state ); }
    ~pthreadState()     { PyGILState_Release( _state ); }
    
private:
    PyGILState_STATE _state; /* Thread state object */
};

/**
 * Structure used by the main thread to allow threads to activate and run. 
 */
struct pthreadSwitch
{
    pthreadSwitch()     {_state = PyEval_SaveThread();}
    ~pthreadSwitch()   {PyEval_RestoreThread(_state);}

private:
    PyThreadState* _state; /* Thread state object */
};

/** Structure holding all relative information for the operation of the python
 * interpreter, variables are pointers so that communication can be achieved.
 */
struct interface {
    int *stage;
   
    std::string directory; /* Directory of the service scripts */
    std::string main; /* Script containing the main function */
    
    input *payload; /* Generic input variable holding payload information */
    int *program_status; /* HTTPcode to return if non syntax errors occurs */ 
    std::string *output; /* Contains the output of the program */

    interface( int* s ): stage( new int(1) ), payload( NULL ),
    program_status( s ), output( NULL ){};
    ~interface()
    { program_status = NULL; delete stage; delete payload; delete output; };
};


#endif /* PYTHONSTRUCTURES_H */

