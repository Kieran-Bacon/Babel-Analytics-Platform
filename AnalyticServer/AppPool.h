#ifndef APPPOOL_H
#define APPPOOL_H

#include <cstring>
#include <mutex>

#include "Engine.h"
#include "rEngine.h"
#include "pEngine.h"
#include "ServiceDefinition.h"
#include "log1.h"
#include "PoolStructures.h"

/**
 * Maintains a number of engines and is responsible supplying engines to
 * requests.
 */
class AppPool
{ 
public:
    /**
     * Default initialise pool parameters.
     */
    AppPool():Service_Definition( NULL ), pool( NULL ), status( POOL::START ){};
    
    /**
     * Trigger the destruction of pool structures.
     */
    ~AppPool(){ delete Service_Definition; delete pool; }
    
    /**
     * Access the Service configuration and populate the application with
     * engines with those specifications.
     * @param configFileAddress - Address of service configuration file.
     * @return status - Indicating success or error code.
     */
    int initializePool(const std::string & configFileAddress);
    
    /**
     * Empty the pool of queueElements.
     * To be used only when the service is being made inactive or when being
     * deleted.
     * @return status - Indicates if the process was possible.
     */
    int emptyPool();
    
    /**
     * Safely handle collection of an engine from the pool, or create new 
     * engine. 
     * @return Returning a child engine class that is being cast as super class. 
     */
    Engine* getApp();
    
    /**
     * Generates and initialise a new Engine that is sent to insertListElement.
     * @return status - Indicating if the engine was created successfully.
     */
    int appendNewApp();
    
    /**
     * Assess the validity of a used engine, if valid send to insertListElement.
     * If not possible, call appendNewApp to create new engine.
     * @param eng - After being executed by message, engine is returned.
     * @return status - Indicating if insertion was successful.
     */
    int appendNewApp( Engine* eng );
    
    /**
     * Get the http code set in the configuration file. Indicating whether the
     * content of GET_HTML is a URL redirect or a html file content.
     * @return http code - Status to accompany the response.
     */
    int GET_status();
    
    /**
     * Get the content to represent this service, either URL redirect location
     * or html file.
     * @return content - string containing file content or URL.
     */
    std::string GET_HTML();
    
    /**
     * Get the current status of the Application pool.
     * @return status - Enum pool status obect representing the condition of
     * the pool.
     */
    POOL::STATUS getStatus();
    
    /**
     * Get the working directory of the service.
     * @return filepath - A file path to the directory.
     */
    std::string getWorkingDirectory();
    
    /**
     * Safely sets the status of the Application pool.
     * @param status - status to set. 
     */
    void setStatus( POOL::STATUS );
    
private:
    
    /**
     * Create a new pool tailored engine object and return. 
     * @return engine - new child engine.
     */
    Engine* createApp();
    
    /**
     * Create an queue element structure and safely insert it into the queue.
     * @param eng - Engine being stored in the queue.
     * @return status - Always success as critical function.
     */
    int insertListElement( Engine* );
    
    ServiceDefinition *Service_Definition;  /* Structure holding service info */
    poolQueue *pool; /* Structure holding linked list of engines */
    POOL::STATUS status; /* Status of the engine */
    std::mutex configLock, poolLock; /* locks to ensure thread safety */
};

#endif  /*APPPOOL_H*/

