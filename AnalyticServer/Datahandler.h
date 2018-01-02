#ifndef DATAHANDLER
#define DATAHANDLER

#include "log1.h"
#include "AppPool.h"
#include "sys/stat.h"
#include <boost/filesystem.hpp>
#include "DataStructures.h"

using namespace libconfig;

class Datahandler
{
public:
    Datahandler( std::string );
    virtual ~Datahandler();
    
    static Datahandler* getInstance();
    static int ensureDirectory( std::string );
    
    static int loadInConfig( const std::string& address, int aPort, int mPort,
                             const std::string&  logLocation );
    static int addToConfig( const std::string& resource,
                            const std::string& status,
                            const std::string& configPath );
    static int removeFromConfig( const std::string& resource );
    
    
    static loggingParameters* getLogging();
    static serverParameters* getAnalytics();
    static serverParameters* getManagement();
    static serviceDirectory* getServices();
    
    static int validate( const std::string& name );
    static permissions::level authenticate( const std::string& key);
    
    static int setLogging( loggingParameters* );
    static int setAnalytics( serverParameters* );
    static int setManagement( serverParameters* );
    static int setServices( serviceDirectory* );
    
    std::string config_Address;
    loggingParameters *logging_param;
    serverParameters *analytics_param, *management_param;
    serviceDirectory *services_param;
    userbank *users;
    permissions *permission_keys;
    
private:
    static int setUserbank( userbank* );
    static int setPermissions( permissions* );
    
    static Datahandler *instance;
};

#endif /* DATAHANDLER */

