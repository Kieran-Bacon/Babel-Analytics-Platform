#ifndef ENGINESTRUCTURES_H
#define ENGINESTRUCTURES_H

/**
 * Engine Status structure. Used to indicate the current stage of an engine.
 */
struct ENGINE {
    enum Status {
        OK               =  0,
        CONNECTION_ERROR = -1,
        SESSION_ERROR    = -2,
        EXECUTE_ERROR    = -3,
    };
};

/**
 * The generic input structure to be acted on my all child engines.
 */
struct input {
    int length;
    std::string *type;
    std::string *variables;
    
    input(): length(0), type( NULL ), variables( NULL ) {}
    ~input(){ type->clear(); variables->clear() ;}
};

#endif /* ENGINESTRUCTURES_H */

