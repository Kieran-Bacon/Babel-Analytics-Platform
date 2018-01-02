#ifndef POOLSTRUCTURES_H
#define POOLSTRUCTURES_H

#include "Engine.h"

struct POOL {
    enum STATUS {
        START = 1,
        STOP = 2,
        ACTIVE = 0,
        INACTIVE = -1,
        SERDEF_ERROR = -2,
        ERROR = -3,
        DYING = -4
    };

    /**
     * Convert a string into a pool status enum.
     * @param status - The status in string form.
     * @return status - the status in pool status enum.
     */
    static POOL::STATUS parseAppStatus( const std::string& status ){
        if( status == "START" )             return POOL::START;
        else if ( status == "STOP")         return POOL::STOP;
        else if ( status == "ACTIVE")       return POOL::ACTIVE;
        else if ( status == "INACTIVE")     return POOL::INACTIVE;
        else if ( status == "SERDEF_ERROR") return POOL::SERDEF_ERROR;
        else                                return POOL::ERROR;
    }

    /**
     * Convert a pool status enum into a string.
     * @param status - The status in pool status enum form.
     * @return status - the status in string form.
     */
    static std::string stringifyStatus( POOL::STATUS status ){
        if ( status == POOL::START )             return "START";
        else if ( status == POOL::STOP )         return "STOP";
        else if ( status == POOL::ACTIVE )       return "ACTIVE";
        else if ( status == POOL::INACTIVE )     return "INACTIVE";
        else if ( status == POOL::SERDEF_ERROR ) return "SERDEF_ERROR";
        else                                     return "ERROR";
    }
};

/**
 * Structure to hold an engine to form a linked list.
 */
struct queueElement {        
    Engine *app;
    queueElement *next;
    
    ~queueElement()
    { delete app; next = NULL; }
};

/**
 * Wrapper structure around linked queueElements.
 */
struct poolQueue {
    int currentSize;
    queueElement *first_element, *last_element;
    
    poolQueue(): currentSize(0), first_element( NULL ), last_element( NULL ){};
    
    ~poolQueue(){
        queueElement *current = first_element;
        while( current != NULL ){
            queueElement *temp = current->next;
            delete current;
            current = temp;
        }
        first_element = NULL;
        last_element = NULL;
    }
};

#endif /* POOLSTRUCTURES_H */

