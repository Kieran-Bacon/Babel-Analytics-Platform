#include "AppPool.h"

int AppPool::initializePool(const std::string & configFileAddress)
{
    ServiceDefinition *newSD = new ServiceDefinition;
    poolQueue *newPQ = new poolQueue;
    
    // Read in service information from configuration file.
    if ( newSD->readConfigFile( configFileAddress ) != 0 ){
        FILE_LOG(logDEBUG1) 
            << "Error reading service configuration file:" << configFileAddress;
        return 1;
    }
    
    configLock.lock(); poolLock.lock();
    // Delete old information if pool is being restarted.
    if( Service_Definition != NULL ) delete Service_Definition;
    if( pool != NULL ) delete pool;
    
    // Assign structures.
    Service_Definition = newSD;
    pool = newPQ;
    
    configLock.unlock(); poolLock.unlock();
    
    
    //Initialise the applications for the pool    
    for (int i = 0; i < Service_Definition->poolSize; i++){
        int n = appendNewApp();
        if (n)
        {
            //Error type and cause defined and raised in appendNewApp();
            FILE_LOG(logDEBUG1) 
                << "Aborting initialisation of AppPool.";
            return(n);
        }
    }
    return 0;
}

int AppPool::emptyPool(){
    poolLock.lock();
    delete pool;
    pool = NULL;
    poolLock.unlock();
}

Engine * AppPool::createApp()
{
    Engine * newApp;
    switch (Service_Definition->type){
        case ServiceDefinition::serviceType::R:
            newApp = new rEngine();
            break;
        case ServiceDefinition::serviceType::PYTHON:
            newApp = new pEngine();
            break;
    };
    return newApp;
}

Engine * AppPool::getApp()
{   
    poolLock.lock();
    if( status == POOL::ACTIVE ){
        if( pool->first_element == NULL ){
            // Unlock, no conflict possible.
            poolLock.unlock();
            // No Engines are currently stored in the queue
            FILE_LOG( logWARNING ) 
                << "The Application Pool has been exhausted." << nli()
                << "Commencing JIT application initialisation....";
            // Create a new engine for this thread and pass it back.
            Engine* block = createApp();
            block->initialise( Service_Definition->workingDirectory,
                               Service_Definition->mainScript );
            return block;
        } else  {

            // Gain a lock on the pool extract a queue element.
            Engine *extractedApp = pool->first_element->app;
            queueElement *temp = pool->first_element;
            pool->first_element = pool->first_element->next;
            pool->currentSize--;
            poolLock.unlock();

            //Delete structure holding Engine and return Engine.
            temp->app = NULL;
            delete temp;
            return extractedApp;
        }
    } else {
        // Application pool is inactive
        poolLock.unlock();
        return (Engine*) NULL;
    }
}

int AppPool::appendNewApp( Engine *usedEng )
{
    if( usedEng->status == ENGINE::OK && usedEng->http_code == 200){
        usedEng->reset();
        return insertListElement( usedEng );
    } else {
        delete usedEng;
        return appendNewApp();
    }
}

int AppPool::appendNewApp()
{
    // New engine must be started and initialised.
    Engine *newApp = createApp();
        
    if( newApp->status == ENGINE::OK ){
        // Initialise the engine.
        int n = newApp->initialise( Service_Definition->workingDirectory, 
                                    Service_Definition->mainScript );
        if(n) return n;
        return insertListElement( newApp );
    }
    // Engine is not started in a constructed correctly.
    return -1;
}

int AppPool::insertListElement( Engine *eng )
{
    // Create queue element to store engine.
    queueElement *newElement = new queueElement{eng, NULL};
    
    // Gain lock.
    poolLock.lock();
    if( status == POOL::ACTIVE && pool->currentSize < Service_Definition->poolSize ){
        // Pool is active and accepting queueElements
        if( pool->first_element != NULL ){
            // Elements exist inside the queue therefore first and last are set.
            // Simply append element to end of linked list.
            pool->last_element->next = newElement;
        } else {
            // Empty list therefore first element becomes new queue element.
            pool->first_element = newElement;
        }
        
        // New element will always be the last element however.
        pool->last_element = newElement;
        pool->currentSize++;
        
        poolLock.unlock();
    } else {
        
        poolLock.unlock();
        // Pool not accepting apps, therefore delete engine and queue element
        // structure.
        delete newElement;
    }
    return 0;
}

int AppPool::GET_status(){
    return Service_Definition->HTTP_Status;
}

std::string AppPool::GET_HTML(){
    return Service_Definition->GET_HTML;
}

POOL::STATUS AppPool::getStatus() {
    return status;
}

std::string AppPool::getWorkingDirectory(){
    return Service_Definition->workingDirectory;
}

void AppPool::setStatus( POOL::STATUS newStatus ){
    poolLock.lock();
    status = newStatus;
    poolLock.unlock();
}