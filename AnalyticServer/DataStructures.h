#ifndef DATASTRUCTURES_H
#define DATASTRUCTURES_H

#include "AppPool.h"

struct loggingParameters {
    std::string root_directory;
    std::string detail_level;
};

struct serverParameters {
    int bufferSize;
    int queueSize;
    int portNum;
    std::string protocol;
};

struct userbank {
    
    userbank( int len, std::string *names): length( len ), usernames( names ){}
    
    int validate( const std::string& name ){
        for( int i = 0; i < length; i++ ){
            if( name == usernames[i] ) return 0;
        }
        return -1;
    }
    
private:
    int length;
    std::string *usernames;
};

struct permissions {
    
    enum level {
        ADMIN = 3,
        LEVELONE = 2,
        LEVELTWO = 1,
        DENIED = 0
    };
    
    permissions( const std::string& a, 
                 const std::string& o,
                 const std::string& t )
                 :admin(a), levelOne(o), levelTwo(t) {}
    
    level authenticate( const std::string& key ){
        if( key == admin )        return level::ADMIN;
        else if( key == levelOne) return level::LEVELONE;
        else if( key == levelTwo) return level::LEVELTWO;
        else                      return level::DENIED;
    }

private:
    std::string admin;
    std::string levelOne;
    std::string levelTwo;
};

struct serviceDirectory {
    std::string root_directory;
    int num_defined;
    std::string *resourceName;
    std::string *configAddress;
    AppPool **applicationPool;

    //constructor
    serviceDirectory( const std::string& dir, int N):
    root_directory( dir ),
    num_defined( N ),
    configAddress( new std::string[N] ),
    resourceName(new std::string[N]),
    applicationPool(new AppPool*[N])
    {}

    //destructor
    //note - AppPools not deleted.
    ~serviceDirectory()
    {delete[] resourceName; delete[] applicationPool;}
};

#endif /* DATASTRUCTURES_H */

