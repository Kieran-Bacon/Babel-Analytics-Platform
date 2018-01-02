#ifndef BINSTRUCTURES_H
#define BINSTRUCTURES_H

#include "AppPool.h"

struct binItem {
    std::string workingDirectory;
    std::string resource;
    std::string config;
    AppPool *pool;
    
    binItem *next;
    
    binItem( 
    const std::string& w, const std::string& r, const std::string& c, AppPool *p
    ):
    workingDirectory( w ), resource( r ), config( c ), pool( p ), next( NULL ){}
    ~binItem(){ 
        workingDirectory.clear(), resource.clear(); config.clear(); 
        delete pool; next = NULL; 
    }
};

struct bin{
    binItem *first;
    binItem *last;
    
    bin(): first( NULL ), last( NULL ){}
};



#endif /* BINSTRUCTURES_H */

