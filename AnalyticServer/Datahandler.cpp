#include "Datahandler.h"

Datahandler *Datahandler::instance = 0;

Datahandler::Datahandler( std::string fileAddress ){
    config_Address = fileAddress;
    logging_param = NULL;
    analytics_param = NULL;
    management_param = NULL;
    services_param = NULL;
    permission_keys = NULL;
};

Datahandler::~Datahandler(){};

Datahandler* Datahandler::getInstance(){
    if( Datahandler::instance != 0 ) return Datahandler::instance;
    else {
        FILE_LOG( logINFO ) << "TODO :: DATAHANDLER.cpp instance is not defined"
                << "Either exit as error on data or try and make a new one or"
                << "something";
    }
}

int Datahandler::ensureDirectory(std::string Address){
    struct stat buffer;   
    if (stat (Address.c_str(), &buffer) == 0){  //test if file exists
        return 0;
    } else {
        return boost::filesystem::create_directories( Address );
    }
}

int Datahandler::loadInConfig( const std::string& fileAddress, 
        int aPort, int mPort, const std::string& logLocation )
{
    if ( Datahandler::instance != 0 ) delete Datahandler::instance;
    Datahandler::instance = new Datahandler( fileAddress );
    loggingParameters *logging_Config = new loggingParameters;
    serverParameters *analytics_Config = new serverParameters;
    serverParameters *management_Config = new serverParameters;
    
    try {
        /* Read in information from the master configuration and place in
         * separate configuration setting objects.
         */
        Config masterConfig;
        masterConfig.readFile(fileAddress.c_str());
        Setting& root = masterConfig.getRoot();
                
        FILE_LOG( logINFO ) << "Master configuration information accessed.";

        Setting& logInfo = root["Logging"];
        Setting& Analytic_Settings = root["Analytic_Settings"];
        Setting& Management_Settings = root["Management_Settings"];
        Setting& usernames = root["Management_Settings"]["usernames"];
        Setting& Auth_Keys = root["Management_Settings"]["permission_keys"];
        Setting& services_info = root["Analytic_Settings"]["service_info"];
        Setting& services = root["Analytic_Settings"]["service_info"]["services"];
        
        //Logging infomation
        if( logLocation == "" )
        logInfo.lookupValue("root_directory", logging_Config->root_directory);
        else logging_Config->root_directory = logLocation;
        logInfo.lookupValue("detail_level" , logging_Config->detail_level);
        
        if (Datahandler::ensureDirectory( logging_Config->root_directory ) != 0){
            FILE_LOG( logERROR )
                << "Error on ensuring directory " << logging_Config->root_directory;
            return -1;
        }
        
        try {
            FILELog::ReportingLevel() = FILELog::FromString(logging_Config->detail_level);
        } catch(const std::exception& e){
            FILE_LOG(logERROR) << e.what();
        }
        
        // Analytic Server information
        Analytic_Settings.lookupValue("bufferSize", analytics_Config->bufferSize);
        Analytic_Settings.lookupValue("queueSize", analytics_Config->queueSize);
        if( aPort == 0 )
        Analytic_Settings.lookupValue("portNum", analytics_Config->portNum);
        else analytics_Config->portNum = aPort;
        Analytic_Settings.lookupValue("protocol", analytics_Config->protocol);
        
        FILE_LOG( logINFO ) 
            << "Analytics Thread's configuration definitions"
            << nli() << "bufferSize: " << analytics_Config->bufferSize
            << nli() << "queueSize: " << analytics_Config->queueSize
            << nli() << "portNum: " << analytics_Config->portNum
            << nli() << "protocol: " << analytics_Config->protocol;
        
        // Management Server Info
        Management_Settings.lookupValue("bufferSize", management_Config->bufferSize);
        Management_Settings.lookupValue("queueSize", management_Config->queueSize);
        if( mPort == 0 )
        Management_Settings.lookupValue("portNum", management_Config->portNum);
        else management_Config->portNum = mPort;
        
        FILE_LOG( logINFO ) 
            << "Management Thread's configuration definitions:"
            << nli() << "bufferSize: " << management_Config->bufferSize
            << nli() << "queueSize: " << management_Config->queueSize
            << nli() << "portNum: " << management_Config->portNum;
        
        // Username Info.
        
        std::string *userarray = new std::string[ usernames.getLength() ]; 
        userbank *validUsers = new userbank( usernames.getLength(), userarray );
        
        for( int j = 0; j < usernames.getLength(); j++ ){
            userarray[j] = usernames[j].c_str();
        }
        
        // Authentication Info.
        std::string admin, level1, level2;
        Auth_Keys.lookupValue( "admin", admin );
        Auth_Keys.lookupValue( "level_one", level1);
        Auth_Keys.lookupValue( "level_two", level2);
        permissions *authentication = new permissions( admin, level1, level2 );
        
        // Services Directory info
        int n = services.getLength();
        std::string serviceRoot;
        services_info.lookupValue("root_directory", serviceRoot);
        serviceDirectory *services_Config = new serviceDirectory( serviceRoot, n );
        
        
        if (Datahandler::ensureDirectory( services_Config->root_directory ) != 0){
            FILE_LOG( logERROR )
                << "Error on ensuring directory " << services_Config->root_directory;
            return -1;
        }
        
        //Loop over services array
        std::string status;
        for (int i = 0; i < n; i++) {
            Setting& single_service = services[i];
            
            //Resource name
            single_service.lookupValue("resource",services_Config->resourceName[i]);
            single_service.lookupValue("status",status);
            single_service.lookupValue("configPath",services_Config->configAddress[i]);
            
            AppPool *pool = new AppPool();
            if( POOL::parseAppStatus( status ) == POOL::ACTIVE ){
                pool->setStatus( POOL::START );
            } else {
                pool->setStatus( POOL::parseAppStatus( status ) );
            }
            
            services_Config->applicationPool[i] = pool;
        }
        
        Datahandler::setLogging( logging_Config );
        Datahandler::setAnalytics( analytics_Config );
        Datahandler::setManagement( management_Config);
        Datahandler::setServices( services_Config );
        Datahandler::setUserbank( validUsers );
        Datahandler::setPermissions( authentication );
        
    } catch(const FileIOException &fioex) {
        FILE_LOG( logERROR ) << "FileIOException raised - Master configuration "
                             << "was not found.";
        return(-1);
    } catch(const ParseException &pex) {
        FILE_LOG( logERROR ) 
            << "ParseException raised - The master configuration file contains a "
            << pex.getError() << " on line " << pex.getLine();
        return(-2);
    } catch (const SettingNotFoundException &nfex) {
        FILE_LOG( logERROR ) << "SettingNotFoundException - Master "
                             << "configuration does not contain the correct "
                             << "information.";
        return(-3);
    }
    
    return 0;
};

int Datahandler::addToConfig(const std::string& resource, 
                             const std::string& status, 
                             const std::string& configPath)
{
    // Get the master configuration file location.
    std::string configAddress = Datahandler::getInstance()->config_Address;
    
    Config master;
    try 
    {
        master.readFile( configAddress.c_str() );
        Setting& root = master.getRoot();

        Setting& services 
            = root["Analytic_Settings"]["service_info"]["services"];
        Setting& service = services.add( Setting::TypeGroup );

        service.add( "resource", Setting::TypeString ) = resource;
        service.add( "status", Setting::TypeString ) = status ;
        service.add( "configPath", Setting::TypeString) = configPath;


        master.writeFile( configAddress.c_str() );
    }
    catch(const FileIOException &fioex)
    {
        FILE_LOG( logERROR ) 
            << "IO Execption raised when trying to add: " << resource;
        return -1;
    }
    catch(const ParseException &pex)
    {
        FILE_LOG( logERROR  ) 
            << "Master config contains an error:" << nli()
            << pex.getLine() << " - " << pex.getError() << nli()
            << "Critical error, must fix before restart!";
        return -2;
    }
    
    return 0;
}

int Datahandler::removeFromConfig(const std::string& resource )
{
    // Get the master configuration file location.
    std::string configAddress = Datahandler::getInstance()->config_Address;
    
    Config master;
    try 
    {
        master.readFile( configAddress.c_str() );
        
        Setting& root = master.getRoot();
        Setting& services 
                = root["Analytic_Settings"]["service_info"]["services"];
        
        int i;
        std::string holder;
        for( i = 0; i < services.getLength(); i++){
            Setting& service = services[i];
            service.lookupValue( "resource", holder);
            if( resource == holder ){
                    break;
            }
        }
        
        if( i != services.getLength() ) services.remove(i);
        else
        { 
            FILE_LOG( logWARNING ) << "Could not remove " << resource 
                << " from config. Not found."; 
        }
        
        master.writeFile( configAddress.c_str() );
    }
    catch(const FileIOException &fioex)
    {
        FILE_LOG( logERROR ) 
            << "IO Execption raised when trying to add: " << resource;
        return -1;
    }
    catch(const ParseException &pex)
    {
        FILE_LOG( logERROR  ) 
            << "Master config contains an error:" << nli()
            << pex.getLine() << " - " << pex.getError() << nli()
            << "Critical error, must fix before restart!";
        return -2;
    }
    
    return 0;
}

loggingParameters* Datahandler::getLogging(){
    return Datahandler::instance->logging_param;
};

serverParameters* Datahandler::getAnalytics(){
    return Datahandler::instance->analytics_param;
};

serverParameters* Datahandler::getManagement(){
    return Datahandler::instance->management_param;
};

serviceDirectory* Datahandler::getServices(){
    return Datahandler::instance->services_param;
};

int Datahandler::validate( const std::string& username ){
    return Datahandler::instance->users->validate( username );
}

permissions::level Datahandler::authenticate( const std::string& key ){
    return Datahandler::instance->permission_keys->authenticate( key );
}

int Datahandler::setLogging( loggingParameters* logPointer ){
    //Lock
    delete  Datahandler::instance->logging_param;
    Datahandler::instance->logging_param = logPointer;
    //unlock
    return 0;
};

int Datahandler::setAnalytics( serverParameters* aPointer ){
    delete Datahandler::instance->analytics_param;
    Datahandler::instance->analytics_param = aPointer;
    return 0;
};

int Datahandler::setManagement( serverParameters* mPointer ){
    delete Datahandler::instance->management_param;
    Datahandler::instance->management_param = mPointer;
    return 0;
};

int Datahandler::setServices( serviceDirectory* sPointer ){
    delete Datahandler::instance->services_param;
    Datahandler::instance->services_param = sPointer;
    return 0;
};

int Datahandler::setUserbank( userbank* users ){
    // Set once. Can only be changed when system is restarted.
    Datahandler::instance->users = users;
}

int Datahandler::setPermissions( permissions *authPointer ){
    // Set once. Can only be changed when system is restarted.
    Datahandler::instance->permission_keys = authPointer;
}