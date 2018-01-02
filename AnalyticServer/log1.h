#ifndef __LOG1_H__
#define __LOG1_H__

#include <sstream>
#include <string>
#include <stdio.h>
#include <sys/time.h>
#include <iostream>
#include <fstream>
#include <ctime>

inline std::string NowTime()
{
    char buffer[11];
    time_t t;
    time(&t);
    tm r = {0};
    strftime(buffer, sizeof(buffer), "%X", localtime_r(&t, &r));
    struct timeval tv;
    gettimeofday(&tv, 0);
    char result[100] = {0};
    std::sprintf(result, "%s.%03ld", buffer, (long)tv.tv_usec / 1000); 
    return result;
}

enum TLogLevel
{
    logERROR, 
    logWARNING,
    Management,
    Analytics,
    logINFO, 
    logDEBUG, 
    logDEBUG1, 
    logDEBUG2, 
    logDEBUG3, 
    logDEBUG4
};

class Log
{
public:
    Log();
    virtual ~Log();
    std::ostringstream& Get(TLogLevel level = logINFO);
    
    static TLogLevel& ReportingLevel();
    static std::string& logLocation();
    
    static std::string ToString(TLogLevel level);
    static TLogLevel FromString(const std::string& level);
    static std::string nli();
protected:
    std::ostringstream os;
private:
    Log(const Log&);
    Log& operator =(const Log&);
};

inline Log::Log()
{
}

inline std::string nli()
{
    return "\n" + std::string( 20, ' ');
}

inline std::ostringstream& Log::Get(TLogLevel level)
{
    os << ToString(level) << " " << NowTime() << " ";
    return os;
}

inline Log::~Log()
{
    os << std::endl;
    
    if( Log::logLocation() != "" ){
        time_t t = time(0);
        struct tm* now = localtime( &t );
        std::string name = std::to_string(now->tm_mday) 
                         + '-' + std::to_string(now->tm_mon+1) 
                         + '-' + std::to_string( now->tm_year+1900 );
        
        std::ofstream filestream(Log::logLocation() + name, std::ios_base::app);
        if( filestream.is_open() )
        {
            filestream << os.str().c_str();
            filestream.close();
        }
        else 
        {
            fprintf( stderr, "Error on writing to log file.\n" );
            fprintf(stderr, "%s", os.str().c_str());
            fflush(stderr);
        }
    }
    else
    {
        fprintf(stderr, "%s", os.str().c_str());
        fflush(stderr);     
    }
}

inline TLogLevel& Log::ReportingLevel()
{
    static TLogLevel reportingLevel = logDEBUG4;
    return reportingLevel;
}

inline std::string& Log::logLocation()
{
    static std::string location = "";
    return location;
}

inline std::string Log::ToString(TLogLevel level)
{
    static const char* const buffer[] 
        = {"ERROR", "WARNING", "MANAGEMENT", "ANALYTICS", "INFO",
           "DEBUG", "DEBUG1", "DEBUG2", "DEBUG3", "DEBUG4"};
    return buffer[level];
}

inline TLogLevel Log::FromString(const std::string& level)
{
    if (level == "DEBUG4")    return logDEBUG4;
    if (level == "DEBUG3")    return logDEBUG3;
    if (level == "DEBUG2")    return logDEBUG2;
    if (level == "DEBUG1")    return logDEBUG1;
    if (level == "DEBUG")     return logDEBUG;
    if (level == "INFO")      return logINFO;
    if (level == "ANALYTICS") return Analytics;
    if (level == "MANAGEMENT")return Management;
    if (level == "WARNING")   return logWARNING;
    if (level == "ERROR")     return logERROR;
    Log().Get(logWARNING) << "Unknown logging level '" << level << "'. Using INFO level as default.";
    return logINFO;
}

typedef Log FILELog;

#define FILE_LOG(level) \
    if (level > FILELog::ReportingLevel()) ; \
    else Log().Get(level)
#endif //__LOG_H__
