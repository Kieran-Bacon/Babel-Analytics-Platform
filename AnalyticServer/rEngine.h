#ifndef RENGINE_H
#define RENGINE_H

#include "Rconnection.h"

#include "log1.h"
#include "Engine.h"


class rEngine : public Engine
{

private:
	Rconnection *rc;	//Pointer to R connection object
public:
	rEngine();
	~rEngine();

	/*
         * Execute command within R session
         * @param cmd literal string to be parsed by the R interpreter.
         */
        int initialise( const std::string& wd, const std::string& script );
        std::string execute( const std::string& content_type, const std::string& payload );
        int reset();
        std::string runCommand( const std::string& cmd );
};

#endif /*RENGINE_H*/

