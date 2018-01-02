#ifndef HTTPSTRUCTURES_H
#define HTTPSTRUCTURES_H

struct HTTP {
    enum Status {
          READ_ERR=-3
        , SOCKET_ERR=-2
        , ERROR=-1
        , OKAY=0
        , READ_HEADER=1
        , READ_BODY=2
        , COMPLETE=3
        , WAIT=4
    };
    
    enum Method{              
          GET                    
        , HEAD                   
        , POST                   
        , PUT                    
        , DELETE
        , OPTIONS
        , TRACE                  
        , CONNECT  
    };
    
    static std::string stringify( HTTP::Method method ){
        if( method == GET )             return "GET";
        else if( method == HEAD )       return "HEAD";
        else if( method == POST )       return "POST";
        else if( method == PUT )        return "PUT";
        else if( method == DELETE )     return "DELETE";
        else if( method == OPTIONS )    return "OPTIONS";
        else if( method == TRACE )      return "TRACE";
        else if( method == CONNECT )    return "CONNECT";
        else                            return "UNKNOWN";
    }
};

struct generalHeader_t {
    std::string Cache_Control , Connection, Date , Pragma 
    , Trailer , Transfer_Encoding , Upgrade , Via , Warning;   
};

struct entityHeader_t {
    std::string Allow , Content_Encoding , Content_Language
    ,Content_Length , Content_Location , Content_MD5 , Content_Range 
    , Content_Type, Postman_Token , Expires , Last_Modified , extension_header;
};

struct requestHeader_t {
    std::string Accept , Accept_Charset , Accept_Encoding 
    , Accept_Language, Access_Token , Authorization , Expect , From , Host 
    , If_Match , If_Modified_Since , If_None_Match , If_Range 
    , If_Unmodified_Since , Max_Forwards , Username , Proxy_Authorization 
    , Range , Referer , TE , User_Agent;    
};

struct responseHeader_t{
    std::string Accept_Ranges, Age, ETag, Location, Proxy_Authenticate
    , Retry_After, Server, Vary, WWW_Authenticate;
};


#endif /* HTTPSTRUCTURES_H */

