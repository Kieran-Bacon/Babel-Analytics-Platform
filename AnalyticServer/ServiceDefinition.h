#ifndef SERVICEDEFINITION_H
#define	SERVICEDEFINITION_H

#include <string>
#include <sstream>
#include <fstream>
#include <sys/stat.h>


#include "log1.h"
#include <libconfig.h++>

using namespace libconfig;

class ServiceDefinition {
public:    
    int readConfigFile(const std::string& configFilePath);
    
    enum serviceType {R,PYTHON,ERROR};
    
    //--Properties--
    std::string workingDirectory;  //the working directory for the service
    std::string version;
    std::string mainScript; //location of the script defining the service
    serviceType type;   //Type of service.
    int poolSize;   //required size of the application pool.
    int HTTP_Status; //location of generic html service file.
    std::string GET_HTML;   //static html for get requests
private:
    ServiceDefinition::serviceType parseType( std::string );
    int ensureDirectory( std::string );
    int readHTMLFile( std::string );
};

#endif	/* SERVICEDEFINITION_H */

